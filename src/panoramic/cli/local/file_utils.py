import logging
from enum import Enum
from pathlib import Path
from typing import Any, Dict

import yaml

logger = logging.getLogger(__name__)


class FileExtension(Enum):
    """
    Enumeration with all available file extensions
    """

    MODEL_YAML = '.model.yaml'


class FilePackage(Enum):
    """
    Enumeration with all available file packages
    """

    SCANNED = 'scanned'


def get_work_dir_abs_filepath() -> Path:
    """
    Return abs filepath of current workdir
    """
    return Path().absolute()


def get_target_abs_filepath(table_file_name: str, file_extension: FileExtension, file_package: FilePackage) -> Path:
    """
    Get target file abs filepath
    """
    file_name = f'{table_file_name}{file_extension.value}'
    return get_work_dir_abs_filepath() / file_package.value / file_name


def ensure_dir(abs_filepath: Path):
    """
    Ensure parent directory exists.
    """
    path_obj = abs_filepath.parent
    path_obj.mkdir(parents=True, exist_ok=True)


def write_yaml(abs_filepath: Path, yaml_dict: Dict[str, Any]):
    """
    Writes yaml dict to path
    """
    logger.debug(f'Write yaml {abs_filepath}')
    ensure_dir(abs_filepath)
    with open(abs_filepath, 'w') as f:
        yaml.dump(yaml_dict, f, default_flow_style=False)


def read_yaml(abs_filepath: str) -> Dict[str, Any]:
    """
    Reads yaml dict from path
    """
    logger.debug(f'Read yaml {abs_filepath}')
    with open(abs_filepath, 'r') as f:
        return yaml.safe_load(f)


def delete_file(abs_filepath: Path):
    """Delete file at given path."""
    # TODO: check file exists before deleting it
    abs_filepath.unlink()
