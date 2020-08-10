import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Optional

import click
from tqdm import tqdm

from panoramic.cli.companies.client import CompaniesClient
from panoramic.cli.context import get_company_slug
from panoramic.cli.controller import reconcile
from panoramic.cli.local import get_state as get_local_state
from panoramic.cli.local.executor import LocalExecutor
from panoramic.cli.local.file_utils import Paths, write_yaml
from panoramic.cli.local.writer import FileWriter
from panoramic.cli.logging import echo_error, echo_info
from panoramic.cli.parser import load_scanned_tables
from panoramic.cli.physical_data_source.client import PhysicalDataSourceClient
from panoramic.cli.refresh import Refresher
from panoramic.cli.remote import get_state as get_remote_state
from panoramic.cli.remote.executor import RemoteExecutor
from panoramic.cli.scan import Scanner

logger = logging.getLogger(__name__)


def configure():
    """Global configuration for CLI."""
    client_id = click.prompt('Enter your client id', type=str)
    client_secret = click.prompt('Enter your client secret', hide_input=True, type=str)

    config_file = Paths.config_file()
    if not config_file.parent.exists():
        config_file.parent.mkdir()

    write_yaml(config_file, {'client_id': client_id, 'client_secret': client_secret})


def initialize():
    """Initialize context."""
    client = CompaniesClient()

    try:
        companies = client.get_companies()
    except Exception:
        logger.debug('Failed to fetch available companies', exc_info=True)
        companies = []

    base_text = 'Enter your company slug'
    if len(companies) == 0:
        prompt_text = base_text
    elif len(companies) > 3:
        prompt_text = f'{base_text} (Available - {{{",".join(list(companies)[:3])}}},...)'
    else:
        prompt_text = f'{base_text} (Available - {{{",".join(companies)}}})'

    company_slug = click.prompt(prompt_text, type=str, default=next(iter(companies), None))
    write_yaml(Paths.context_file(), {'company_slug': company_slug, 'api_version': 'v1'})


def list_connections():
    client = PhysicalDataSourceClient()

    sources = client.get_sources(get_company_slug())
    if len(sources) == 0:
        echo_error('No data connections have been found')
    else:
        for source in client.get_sources(get_company_slug()):
            echo_info(source['source_name'])


def list_companies():
    client = CompaniesClient()
    companies = client.get_companies()
    if len(companies) == 0:
        echo_error('No companies have been found')
    else:
        for company in companies:
            echo_info(company)


def scan(source_id: str, table_filter: Optional[str], parallel: int = 1):
    """Scan all metadata for given source and filter."""
    company_slug = get_company_slug()
    scanner = Scanner(company_slug, source_id)
    scanner.fetch_token()

    tables = list(scanner.scan_tables(table_filter=table_filter))

    if len(tables) == 0:
        echo_info('No tables have been found')
        return

    refresher = Refresher(company_slug, source_id)
    refresher.fetch_token()
    writer = FileWriter()

    progress_bar = tqdm(total=len(tables))

    def _process_table(table: Dict[str, Any]):
        # drop source name from schema
        sourceless_schema = table['table_schema'].split('.', 1)[1]
        table_name = f'{sourceless_schema}.{table["table_name"]}'

        try:
            refresher.refresh_table(table_name)
            raw_columns = scanner.scan_columns(table_filter=table_name)
            for model in load_scanned_tables(raw_columns):
                writer.write_scanned_model(model)
                echo_info(f'Discovered model {model.model_name}')
        except Exception:
            error_msg = f'Metadata could not be scanned for table {table_name}'
            echo_error(error_msg)
            logger.debug(error_msg, exc_info=True)
        finally:
            progress_bar.update()

    executor = ThreadPoolExecutor(max_workers=parallel)
    for _ in executor.map(_process_table, tables):
        pass

    progress_bar.write(f'Scanned {progress_bar.total} tables')


def pull():
    """Pull models and data sources from remote."""
    company_slug = get_company_slug()
    remote_state = get_remote_state(company_slug)
    local_state = get_local_state()

    actions = reconcile(local_state, remote_state)

    if len(actions.actions) == 0:
        echo_info('No configuration has been published')
        return

    executor = LocalExecutor()

    with tqdm(actions.actions) as bar:
        for action in bar:
            try:
                executor.execute(action)
            except Exception:
                error_msg = f'Failed to execute action {action.description}'
                echo_error(error_msg)
                logger.debug(error_msg, exc_info=True)
        bar.write(f'Pulled {bar.total} configurations')


def push():
    """Push models and data sources to remote."""
    company_slug = get_company_slug()
    remote_state = get_remote_state(company_slug)
    local_state = get_local_state()

    actions = reconcile(remote_state, local_state)

    if len(actions.actions) == 0:
        echo_info('No configuration to publish')
        return

    executor = RemoteExecutor(company_slug)

    with tqdm(actions.actions) as bar:
        for action in bar:
            try:
                executor.execute(action)
            except Exception:
                error_msg = f'Failed to execute action {action.description}'
                echo_error(error_msg)
                logger.debug(error_msg, exc_info=True)
        bar.write(f'Updated {bar.total} configurations')
