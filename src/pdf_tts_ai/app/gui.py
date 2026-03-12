from pathlib import Path
import shutil
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .bootstrap import ensure_runtime_dependencies, is_cuda_provider_available, is_piper_available
from ..service import JobRequest, run_job


class PdfTtsApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("PDF TTS AI")
        self.root.geometry("760x470")

        self.pdf_var = tk.StringVar()
        self.model_var = tk.StringVar()
        self.out_base_var = tk.StringVar()
        self.piper_exe_var = tk.StringVar(value=self._default_piper_exe())
        self.min_chars_var = tk.StringVar(value="700")
        self.max_chars_var = tk.StringVar(value="1600")
        self.use_cuda_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="Ready")
        self.progress_var = tk.DoubleVar(value=0.0)
        self.stage_var = tk.StringVar(value="-")

        self._build_layout()

    def _build_layout(self) -> None:
        frame = ttk.Frame(self.root, padding=12)
        frame.pack(fill="both", expand=True)

        self._row_with_browse(frame, 0, "PDF file", self.pdf_var, self._pick_pdf)
        self._row_with_browse(frame, 1, "Piper model", self.model_var, self._pick_model)
        self._row_with_browse(frame, 2, "Piper executable", self.piper_exe_var, self._pick_piper_exe)
        self._row_with_browse(frame, 3, "Output base dir", self.out_base_var, self._pick_out_dir)

        ttk.Label(frame, text="Min chars").grid(row=4, column=0, sticky="w", pady=6)
        ttk.Entry(frame, textvariable=self.min_chars_var, width=12).grid(row=4, column=1, sticky="w", pady=6)

        ttk.Label(frame, text="Max chars").grid(row=5, column=0, sticky="w", pady=6)
        ttk.Entry(frame, textvariable=self.max_chars_var, width=12).grid(row=5, column=1, sticky="w", pady=6)

        ttk.Checkbutton(frame, text="Use GPU (CUDA)", variable=self.use_cuda_var).grid(row=5, column=2, sticky="w", pady=6)

        self.start_button = ttk.Button(frame, text="Start", command=self._start)
        self.start_button.grid(row=6, column=0, sticky="w", pady=10)

        ttk.Label(frame, textvariable=self.status_var).grid(row=6, column=1, sticky="w")

        self.progress = ttk.Progressbar(frame, orient="horizontal", mode="determinate", maximum=100, variable=self.progress_var)
        self.progress.grid(row=7, column=0, columnspan=3, sticky="ew", pady=4)
        ttk.Label(frame, textvariable=self.stage_var).grid(row=8, column=0, columnspan=3, sticky="w")

        self.log = tk.Text(frame, height=10, width=80)
        self.log.grid(row=9, column=0, columnspan=3, sticky="nsew", pady=8)

        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(9, weight=1)

    def _default_piper_exe(self) -> str:
        venv_candidate = Path.cwd() / ".venv" / "Scripts" / "piper.exe"
        if venv_candidate.exists():
            return str(venv_candidate)
        return "piper"

    def _row_with_browse(
        self,
        frame: ttk.Frame,
        row: int,
        label: str,
        variable: tk.StringVar,
        callback,
    ) -> None:
        ttk.Label(frame, text=label).grid(row=row, column=0, sticky="w", pady=6)
        ttk.Entry(frame, textvariable=variable).grid(row=row, column=1, sticky="ew", padx=8, pady=6)
        ttk.Button(frame, text="Browse", command=callback).grid(row=row, column=2, sticky="w", pady=6)

    def _pick_pdf(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
        if path:
            self.pdf_var.set(path)

    def _pick_model(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("ONNX model", "*.onnx"), ("All files", "*.*")])
        if path:
            self.model_var.set(path)

    def _pick_out_dir(self) -> None:
        path = filedialog.askdirectory()
        if path:
            self.out_base_var.set(path)

    def _pick_piper_exe(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("Executable", "*.exe"), ("All files", "*.*")])
        if path:
            self.piper_exe_var.set(path)

    def _resolve_piper_exe(self) -> str | None:
        value = self.piper_exe_var.get().strip() or "piper"
        if value == "piper":
            if is_piper_available():
                return value
            messagebox.showerror("Missing Piper", "Piper executable not found in PATH.")
            return None

        path = Path(value)
        if path.exists():
            return str(path)
        if shutil.which(value):
            return value
        messagebox.showerror("Missing Piper", f"Piper executable not found: {value}")
        return None

    def _start(self) -> None:
        piper_exe = self._resolve_piper_exe()
        if piper_exe is None:
            return
        if self.use_cuda_var.get() and not is_cuda_provider_available():
            messagebox.showerror(
                "CUDA unavailable",
                "CUDA mode was selected, but CUDAExecutionProvider is unavailable in onnxruntime.\n"
                "Install onnxruntime-gpu and verify NVIDIA runtime setup.",
            )
            return

        try:
            request = JobRequest(
                pdf_path=Path(self.pdf_var.get()),
                output_base_dir=Path(self.out_base_var.get()),
                model_path=Path(self.model_var.get()),
                piper_exe=piper_exe,
                use_cuda=self.use_cuda_var.get(),
                min_chars=int(self.min_chars_var.get()),
                max_chars=int(self.max_chars_var.get()),
            )
        except ValueError:
            messagebox.showerror("Invalid input", "Min/Max chars must be valid integers.")
            return

        self.start_button.config(state="disabled")
        self.status_var.set("Running...")
        self.progress_var.set(0)
        self.stage_var.set("Starting")
        self._append_log("Starting job...")

        thread = threading.Thread(target=self._run_job_thread, args=(request,), daemon=True)
        thread.start()

    def _run_job_thread(self, request: JobRequest) -> None:
        def on_progress(percent: int, stage: str) -> None:
            self.root.after(0, self._on_progress, percent, stage)

        try:
            outputs = run_job(request, progress_callback=on_progress)
            self.root.after(0, self._on_success, outputs)
        except Exception as exc:  # noqa: BLE001
            self.root.after(0, self._on_error, str(exc))

    def _on_progress(self, percent: int, stage: str) -> None:
        bounded = max(0, min(100, percent))
        self.progress_var.set(bounded)
        self.stage_var.set(f"{bounded}% - {stage}")

    def _on_success(self, outputs: dict[str, Path]) -> None:
        self.progress_var.set(100)
        self.stage_var.set("100% - Completed")
        self._append_log(f"Done. Merged: {outputs['merged_audio']}")
        self._append_log(f"Manifest: {outputs['manifest']}")
        self.status_var.set("Completed")
        self.start_button.config(state="normal")

    def _on_error(self, message: str) -> None:
        self._append_log(f"Error: {message}")
        self.status_var.set("Failed")
        self.stage_var.set("Failed")
        self.start_button.config(state="normal")
        messagebox.showerror("Pipeline failed", message)

    def _append_log(self, message: str) -> None:
        self.log.insert("end", f"{message}\n")
        self.log.see("end")


def main() -> None:
    ensure_runtime_dependencies(auto_install=True)
    root = tk.Tk()
    PdfTtsApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
