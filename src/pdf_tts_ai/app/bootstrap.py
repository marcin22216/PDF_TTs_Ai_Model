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
    ensure_onnxruntime_for_hardware(auto_install=auto_install)


def is_piper_available() -> bool:
    return shutil.which("piper") is not None


def is_ffmpeg_available(ffmpeg_exe: str = "ffmpeg") -> bool:
    return shutil.which(ffmpeg_exe) is not None


def get_onnxruntime_providers() -> list[str]:
    try:
        ort = importlib.import_module("onnxruntime")
    except ImportError:
        return []
    try:
        providers = ort.get_available_providers()
    except Exception:
        return []
    return list(providers)


def is_cuda_provider_available() -> bool:
    return "CUDAExecutionProvider" in get_onnxruntime_providers()


def has_nvidia_gpu() -> bool:
    if shutil.which("nvidia-smi") is None:
        return False
    try:
        result = subprocess.run(
            ["nvidia-smi", "-L"],
            check=False,
            capture_output=True,
            text=True,
        )
        return result.returncode == 0 and "GPU" in result.stdout
    except Exception:
        return False


def ensure_onnxruntime_for_hardware(*, auto_install: bool = True) -> None:
    providers = get_onnxruntime_providers()
    if providers:
        if has_nvidia_gpu() and "CUDAExecutionProvider" not in providers and auto_install:
            try:
                install_python_requirements(["onnxruntime-gpu"])
            except Exception:
                # Soft-fail: keep CPU runtime, do not block app startup.
                pass
        return

    if not auto_install:
        return

    if has_nvidia_gpu():
        try:
            install_python_requirements(["onnxruntime-gpu"])
            return
        except Exception:
            pass
    install_python_requirements(["onnxruntime"])
