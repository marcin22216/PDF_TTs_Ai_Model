from .app import bootstrap as _impl

REQUIRED_IMPORTS = _impl.REQUIRED_IMPORTS


def missing_python_requirements() -> list[str]:
    return _impl.missing_python_requirements()


def install_python_requirements(requirements: list[str]) -> None:
    _impl.install_python_requirements(requirements)


def ensure_runtime_dependencies(*, auto_install: bool = True) -> None:
    missing = missing_python_requirements()
    if missing and auto_install:
        install_python_requirements(missing)
        missing = missing_python_requirements()
    if missing:
        joined = ", ".join(missing)
        raise RuntimeError(f"Missing Python dependencies: {joined}")


def is_piper_available() -> bool:
    return _impl.is_piper_available()


def is_ffmpeg_available(ffmpeg_exe: str = "ffmpeg") -> bool:
    return _impl.is_ffmpeg_available(ffmpeg_exe)


def get_onnxruntime_providers() -> list[str]:
    return _impl.get_onnxruntime_providers()


def is_cuda_provider_available() -> bool:
    return "CUDAExecutionProvider" in get_onnxruntime_providers()


def has_nvidia_gpu() -> bool:
    return _impl.has_nvidia_gpu()


def ensure_onnxruntime_for_hardware(*, auto_install: bool = True) -> None:
    _impl.ensure_onnxruntime_for_hardware(auto_install=auto_install)


__all__ = [
    "REQUIRED_IMPORTS",
    "missing_python_requirements",
    "install_python_requirements",
    "ensure_runtime_dependencies",
    "is_piper_available",
    "is_ffmpeg_available",
    "get_onnxruntime_providers",
    "is_cuda_provider_available",
    "has_nvidia_gpu",
    "ensure_onnxruntime_for_hardware",
]
