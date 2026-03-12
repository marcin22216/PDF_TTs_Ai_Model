import importlib
import shutil

import pytest

from pdf_tts_ai import bootstrap


def test_missing_python_requirements_detects_missing(monkeypatch) -> None:
    original_import = importlib.import_module

    def fake_import(name: str):
        if name == "fitz":
            raise ImportError("missing")
        return original_import(name)

    monkeypatch.setattr(importlib, "import_module", fake_import)

    missing = bootstrap.missing_python_requirements()
    assert "PyMuPDF>=1.24.0" in missing


def test_ensure_runtime_dependencies_auto_installs(monkeypatch) -> None:
    state = {"calls": 0}

    def fake_missing():
        state["calls"] += 1
        if state["calls"] == 1:
            return ["PyMuPDF>=1.24.0"]
        return []

    installed = {"value": False}

    def fake_install(requirements):
        installed["value"] = True
        assert requirements == ["PyMuPDF>=1.24.0"]

    monkeypatch.setattr(bootstrap, "missing_python_requirements", fake_missing)
    monkeypatch.setattr(bootstrap, "install_python_requirements", fake_install)

    bootstrap.ensure_runtime_dependencies(auto_install=True)
    assert installed["value"] is True


def test_ensure_runtime_dependencies_raises_without_auto_install(monkeypatch) -> None:
    monkeypatch.setattr(
        bootstrap, "missing_python_requirements", lambda: ["PyMuPDF>=1.24.0"]
    )

    with pytest.raises(RuntimeError):
        bootstrap.ensure_runtime_dependencies(auto_install=False)


def test_cuda_provider_detection_true(monkeypatch) -> None:
    monkeypatch.setattr(
        bootstrap, "get_onnxruntime_providers", lambda: ["CPUExecutionProvider", "CUDAExecutionProvider"]
    )
    assert bootstrap.is_cuda_provider_available() is True


def test_cuda_provider_detection_false(monkeypatch) -> None:
    monkeypatch.setattr(bootstrap, "get_onnxruntime_providers", lambda: ["CPUExecutionProvider"])
    assert bootstrap.is_cuda_provider_available() is False


def test_is_ffmpeg_available(monkeypatch) -> None:
    monkeypatch.setattr(shutil, "which", lambda name: "C:\\ffmpeg\\ffmpeg.exe" if name == "ffmpeg" else None)
    assert bootstrap.is_ffmpeg_available() is True
