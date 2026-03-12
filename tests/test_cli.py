from pdf_tts_ai.cli import build_parser


def test_cli_parser_requires_core_args() -> None:
    parser = build_parser()
    args = parser.parse_args(["--pdf", "in.pdf", "--out", "out", "--model", "voice.onnx"])
    assert str(args.pdf) == "in.pdf"
    assert str(args.out) == "out"
    assert str(args.model) == "voice.onnx"
    assert args.cuda is False
    assert args.format == "wav"


def test_cli_parser_supports_cuda_flag() -> None:
    parser = build_parser()
    args = parser.parse_args(["--pdf", "in.pdf", "--out", "out", "--model", "voice.onnx", "--cuda"])
    assert args.cuda is True


def test_cli_parser_supports_format_and_bitrate() -> None:
    parser = build_parser()
    args = parser.parse_args(
        ["--pdf", "in.pdf", "--out", "out", "--model", "voice.onnx", "--format", "mp3", "--bitrate", "96k"]
    )
    assert args.format == "mp3"
    assert args.bitrate == "96k"


def test_cli_parser_supports_keep_temp_chunks_flag() -> None:
    parser = build_parser()
    args = parser.parse_args(["--pdf", "in.pdf", "--out", "out", "--model", "voice.onnx", "--keep-temp-chunks"])
    assert args.keep_temp_chunks is True
