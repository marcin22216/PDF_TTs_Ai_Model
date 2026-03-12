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


def get_onnxruntime_providers() -> list[str]:
    return _impl.get_onnxruntime_providers()


def is_cuda_provider_available() -> bool:
    return "CUDAExecutionProvider" in get_onnxruntime_providers()


__all__ = [
    "REQUIRED_IMPORTS",
    "missing_python_requirements",
    "install_python_requirements",
    "ensure_runtime_dependencies",
    "is_piper_available",
    "get_onnxruntime_providers",
    "is_cuda_provider_available",
]
