from __future__ import annotations

import importlib
import shutil
import subprocess
import sys

REQUIRED_IMPORTS: dict[str, str] = {
    "fitz": "PyMuPDF>=1.24.0",
}


def missing_python_requirements() -> list[str]:
    missing: list[str] = []
    for module_name, package_spec in REQUIRED_IMPORTS.items():
        try:
            importlib.import_module(module_name)
        except ImportError:
            missing.append(package_spec)
    return missing


def install_python_requirements(requirements: list[str]) -> None:
    if not requirements:
        return
    subprocess.run(
        [sys.executable, "-m", "pip", "install", *requirements],
        check=True,
        capture_output=True,
        text=True,
    )


def ensure_runtime_dependencies(*, auto_install: bool = True) -> None:
    missing = missing_python_requirements()
    if missing and auto_install:
        install_python_requirements(missing)
        missing = missing_python_requirements()
    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(f"Missing Python dependencies: {joined}")


def is_piper_available() -> bool:
    return shutil.which("piper") is not None
