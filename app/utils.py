"""Utility functions."""

import os
from pathlib import Path


def get_project_root() -> Path:
    project_root = Path(__file__).resolve().parent
    while not (project_root / '.gitignore').exists() and project_root != project_root.parent:
        project_root = project_root.parent
        
    return project_root


def get_env_file_path(envfile: str = '.env'):
    return os.getenv('ENV_FILE_PATH', f'{get_project_root()}/{envfile}')
