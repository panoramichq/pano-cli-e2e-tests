from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from panoramic.cli.local.file_utils import read_yaml
from panoramic.cli.paths import FileExtension, PresetFileName, SystemDirectory


class FilePackage:

    name: str
    data_source_file: Path
    model_files: List[Path]

    def __init__(self, *, name: str, data_source_file: Path, model_files: List[Path]):
        self.name = name
        self.data_source_file = data_source_file
        self.model_files = model_files

    def read_data_source(self) -> Dict[str, Any]:
        """Parse data source file."""
        return read_yaml(self.data_source_file)

    def read_models(self) -> Iterable[Dict[str, Any]]:
        """Parse model files."""
        for f in self.model_files:
            yield read_yaml(f)


class FileReader:

    cwd: Path

    def __init__(self, *, cwd: Optional[Path] = None):
        if cwd is None:
            cwd = Path.cwd()

        self.cwd = cwd

    def _is_system_dir(self, path: Path) -> bool:
        """True when directory is a system directory."""
        return path.name in {d.value for d in SystemDirectory}

    def _has_data_source_file(self, path: Path) -> bool:
        """True when directory contains data source file."""
        return (path / PresetFileName.DATASET_YAML.value).exists()

    def get_packages(self) -> Iterable[FilePackage]:
        """List of packages available in push/pull directory."""
        package_dirs = (
            f for f in self.cwd.iterdir() if f.is_dir() and not self._is_system_dir(f) and self._has_data_source_file(f)
        )
        return (
            FilePackage(
                name=d.name,
                data_source_file=d / PresetFileName.DATASET_YAML.value,
                model_files=list(d.glob(f'*{FileExtension.MODEL_YAML.value}')),
            )
            for d in package_dirs
        )
