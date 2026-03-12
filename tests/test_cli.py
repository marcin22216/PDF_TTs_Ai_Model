from pdf_tts_ai.cli import build_parser


def test_cli_parser_requires_core_args() -> None:
    parser = build_parser()
    args = parser.parse_args(["--pdf", "in.pdf", "--out", "out", "--model", "voice.onnx"])
    assert str(args.pdf) == "in.pdf"
    assert str(args.out) == "out"
    assert str(args.model) == "voice.onnx"
