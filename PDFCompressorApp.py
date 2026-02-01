#!/usr/bin/env python3
"""
PDF Toolkit - Modern UI Edition
==================================
Features:
- Clean, Flat Dark UI
- Large readable typography
- Drag & Drop support
- Robust Ghostscript handling
"""

import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import subprocess
import os
import threading
import sys
import glob
import time


# ============================================================================
# LOGIC / GHOSTSCRIPT (Unchanged)
# ============================================================================

def find_ghostscript():
    """Find Ghostscript executable."""
    import shutil
    # Check PATH
    for cmd in ["gswin64c", "gswin32c", "gs"]:
        path = shutil.which(cmd)
        if path: return path

    # Check Common Windows Paths
    if sys.platform == 'win32':
        search_paths = [
            r"C:\Program Files\gs\*\bin\gswin64c.exe",
            r"C:\Program Files (x86)\gs\*\bin\gswin32c.exe",
            os.path.expanduser(r"~\AppData\Local\Programs\gs\*\bin\gswin64c.exe"),
        ]
        for pattern in search_paths:
            matches = glob.glob(pattern)
            if matches: return sorted(matches)[-1]

    # Check Mac
    elif sys.platform == 'darwin':
        for p in ["/usr/local/bin/gs", "/opt/homebrew/bin/gs"]:
            if os.path.exists(p): return p
    return None


def get_ghostscript_version(gs_path):
    try:
        res = subprocess.run([gs_path, "--version"], capture_output=True, text=True, timeout=2)
        return res.stdout.strip() if res.returncode == 0 else "Unknown"
    except:
        return "Unknown"


def run_gs(cmd, input_ref, output_path):
    try:
        if not input_ref: return {"success": False, "error": "No input files"}

        # Determine original size for stats
        if isinstance(input_ref, list):
            original_size = sum(os.path.getsize(f) for f in input_ref)
        else:
            original_size = os.path.getsize(input_ref)

        result = subprocess.run([c for c in cmd if c], capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            return {"success": False, "error": result.stderr[:200]}

        if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
            return {"success": False, "error": "Output file empty"}

        new_size = os.path.getsize(output_path)
        reduction = ((original_size - new_size) / original_size) * 100 if original_size > 0 else 0

        return {"success": True, "reduction": reduction}
    except Exception as e:
        return {"success": False, "error": str(e)}


def compress_pdf(inp, out, quality):
    gs = find_ghostscript()
    cmd = [gs, "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.4", f"-dPDFSETTINGS=/{quality}",
           "-dNOPAUSE", "-dBATCH", f"-sOutputFile={out}", inp]
    return run_gs(cmd, inp, out)


def merge_pdfs(inputs, out):
    gs = find_ghostscript()
    cmd = [gs, "-sDEVICE=pdfwrite", "-dNOPAUSE", "-dBATCH", f"-sOutputFile={out}"] + inputs
    return run_gs(cmd, inputs, out)


def split_pdf(inp, out, pages):
    gs = find_ghostscript()
    cmd = [gs, "-sDEVICE=pdfwrite", "-dNOPAUSE", "-dBATCH", f"-sPageList={pages}",
           f"-sOutputFile={out}", inp]
    return run_gs(cmd, inp, out)


# ============================================================================
# MODERN UI CLASS
# ============================================================================

class ModernPDFApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Toolkit Pro")
        self.root.geometry("700x850")
        self.root.minsize(600, 700)

        # --- THEME CONFIGURATION ---
        self.colors = {
            "bg": "#0f172a",  # Deep Blue/Black
            "panel": "#1e293b",  # Card Background
            "input": "#334155",  # Input Field BG
            "primary": "#6366f1",  # Indigo Button
            "hover": "#818cf8",  # Lighter Indigo
            "text": "#f8fafc",  # White text
            "subtext": "#94a3b8",  # Gray text
            "success": "#10b981",
            "error": "#ef4444"
        }

        # Define Fonts
        self.fonts = {
            "h1": ("Segoe UI", 26, "bold"),
            "h2": ("Segoe UI", 16, "bold"),
            "body": ("Segoe UI", 12),
            "mono": ("Consolas", 11),
            "small": ("Segoe UI", 10),
            "icon": ("Segoe UI", 14)
        }

        self.root.configure(bg=self.colors["bg"])

        # Data
        self.files = []
        self.quality_var = tk.StringVar(value="ebook")
        self.merge_name_var = tk.StringVar(value="merged_document")
        self.split_range_var = tk.StringVar(value="1-5")
        self.gs_path = find_ghostscript()

        self.setup_styles()
        self.build_ui()
        self.setup_dnd()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        # Notebook (Tabs) Styling
        style.configure("TNotebook", background=self.colors["bg"], borderwidth=0)
        style.configure("TNotebook.Tab",
                        background=self.colors["panel"],
                        foreground=self.colors["subtext"],
                        font=("Segoe UI", 12, "bold"),
                        padding=[20, 15],
                        borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected", self.colors["primary"])],
                  foreground=[("selected", "white")])

        # Progress Bar
        style.configure("Horizontal.TProgressbar",
                        troughcolor=self.colors["panel"],
                        background=self.colors["success"],
                        thickness=10, borderwidth=0)

    def build_ui(self):
        # MAIN CONTAINER
        main = tk.Frame(self.root, bg=self.colors["bg"])
        main.pack(fill="both", expand=True, padx=40, pady=30)

        # 1. HEADER
        header_frame = tk.Frame(main, bg=self.colors["bg"])
        header_frame.pack(fill="x", pady=(0, 20))

        tk.Label(header_frame, text="📄 PDF Toolkit", font=self.fonts["h1"],
                 fg=self.colors["text"], bg=self.colors["bg"]).pack(side="left")

        # Version/Status Pill
        status_text = f"Ghostscript: {get_ghostscript_version(self.gs_path)}" if self.gs_path else "Ghostscript Missing!"
        status_color = self.colors["success"] if self.gs_path else self.colors["error"]

        tk.Label(header_frame, text=status_text, font=self.fonts["small"],
                 fg=status_color, bg=self.colors["bg"]).pack(side="right", pady=10)

        # 2. FILE MANAGEMENT AREA
        self.build_file_area(main)

        # 3. TABS (Notebook)
        self.notebook = ttk.Notebook(main)
        self.notebook.pack(fill="both", expand=True, pady=20)
        self.notebook.bind("<<NotebookTabChanged>>", self.update_action_button)

        # Tab Frames
        self.tab_shrink = self.create_tab_frame()
        self.tab_merge = self.create_tab_frame()
        self.tab_split = self.create_tab_frame()

        self.notebook.add(self.tab_shrink, text="  Compress  ")
        self.notebook.add(self.tab_merge, text="  Merge  ")
        self.notebook.add(self.tab_split, text="  Split  ")

        # Fill Tab Contents
        self.build_shrink_tab()
        self.build_merge_tab()
        self.build_split_tab()

        # 4. ACTION BUTTON
        self.action_btn = tk.Button(main, text="START PROCESSING", font=("Segoe UI", 13, "bold"),
                                    bg=self.colors["primary"], fg="white",
                                    activebackground=self.colors["hover"], activeforeground="white",
                                    relief="flat", cursor="hand2", pady=15,
                                    command=self.run_process)
        self.action_btn.pack(fill="x", pady=(10, 0))

        # Progress Bar (Hidden initially)
        self.progress_frame = tk.Frame(main, bg=self.colors["bg"])
        self.pbar = ttk.Progressbar(self.progress_frame, style="Horizontal.TProgressbar", mode="determinate")
        self.pbar.pack(fill="x", pady=(10, 5))
        self.p_label = tk.Label(self.progress_frame, text="Ready...", font=self.fonts["small"],
                                fg=self.colors["subtext"], bg=self.colors["bg"])
        self.p_label.pack()

    def create_tab_frame(self):
        """Helper to create consistent tab backgrounds"""
        f = tk.Frame(self.notebook, bg=self.colors["panel"])
        f.pack(fill="both", expand=True)
        return f

    def build_file_area(self, parent):
        """Top section: File list and Drag Drop"""
        container = tk.Frame(parent, bg=self.colors["panel"], padx=2, pady=2)  # Border effect
        container.pack(fill="x", pady=10)

        inner = tk.Frame(container, bg=self.colors["panel"])
        inner.pack(fill="both", expand=True)

        # Listbox
        self.listbox = tk.Listbox(inner, font=self.fonts["mono"],
                                  bg=self.colors["input"], fg=self.colors["text"],
                                  selectbackground=self.colors["primary"],
                                  relief="flat", height=6, borderwidth=10,
                                  highlightthickness=0)
        self.listbox.pack(side="left", fill="both", expand=True)

        # Side Controls
        controls = tk.Frame(inner, bg=self.colors["panel"], padx=10)
        controls.pack(side="right", fill="y")

        def mk_btn(txt, cmd, color=None):
            c = color if color else self.colors["input"]
            tk.Button(controls, text=txt, font=self.fonts["icon"], command=cmd,
                      bg=c, fg=self.colors["text"], relief="flat", width=4,
                      activebackground=self.colors["hover"]).pack(pady=2)

        mk_btn("▲", self.move_up)
        mk_btn("▼", self.move_down)
        mk_btn("🗑", self.clear_list, self.colors["error"])
        mk_btn("✚", self.browse_files, self.colors["primary"])

        # Drop Hint
        self.drop_lbl = tk.Label(parent, text="Drag & Drop PDF files here",
                                 font=self.fonts["small"], fg=self.colors["subtext"], bg=self.colors["bg"])
        self.drop_lbl.pack(pady=(5, 0))

    def build_shrink_tab(self):
        """Content for Compress Tab"""
        wrapper = tk.Frame(self.tab_shrink, bg=self.colors["panel"], padx=30, pady=30)
        wrapper.pack(fill="both", expand=True)

        tk.Label(wrapper, text="Select Quality Level:", font=self.fonts["h2"],
                 fg=self.colors["text"], bg=self.colors["panel"]).pack(anchor="w", pady=(0, 20))

        modes = [
            ("Screen (72dpi)", "screen", "Smallest file size. Good for email/web."),
            ("eBook (150dpi)", "ebook", "Medium quality. Best balance."),
            ("Printer (300dpi)", "printer", "High quality. Good for home printing.")
        ]

        for text, val, desc in modes:
            row = tk.Frame(wrapper, bg=self.colors["panel"], pady=5)
            row.pack(fill="x")

            rb = tk.Radiobutton(row, text=text, variable=self.quality_var, value=val,
                                font=("Segoe UI", 12, "bold"),
                                bg=self.colors["panel"], fg=self.colors["text"],
                                selectcolor=self.colors["bg"], activebackground=self.colors["panel"],
                                highlightthickness=0)
            rb.pack(anchor="w")

            tk.Label(row, text=desc, font=("Segoe UI", 10),
                     fg=self.colors["subtext"], bg=self.colors["panel"]).pack(anchor="w", padx=25)

    def build_merge_tab(self):
        """Content for Merge Tab"""
        wrapper = tk.Frame(self.tab_merge, bg=self.colors["panel"], padx=30, pady=30)
        wrapper.pack(fill="both", expand=True)

        tk.Label(wrapper, text="Output Filename:", font=self.fonts["h2"],
                 fg=self.colors["text"], bg=self.colors["panel"]).pack(anchor="w", pady=(0, 10))

        # Custom Entry styling
        entry_frame = tk.Frame(wrapper, bg=self.colors["input"], padx=10, pady=10)
        entry_frame.pack(fill="x")

        entry = tk.Entry(entry_frame, textvariable=self.merge_name_var,
                         font=self.fonts["body"], bg=self.colors["input"],
                         fg="white", insertbackground="white", relief="flat")
        entry.pack(fill="x")

        tk.Label(wrapper, text=".pdf will be added automatically", font=self.fonts["small"],
                 fg=self.colors["subtext"], bg=self.colors["panel"]).pack(anchor="w", pady=5)

    def build_split_tab(self):
        """Content for Split Tab"""
        wrapper = tk.Frame(self.tab_split, bg=self.colors["panel"], padx=30, pady=30)
        wrapper.pack(fill="both", expand=True)

        tk.Label(wrapper, text="Page Range:", font=self.fonts["h2"],
                 fg=self.colors["text"], bg=self.colors["panel"]).pack(anchor="w", pady=(0, 10))

        entry_frame = tk.Frame(wrapper, bg=self.colors["input"], padx=10, pady=10)
        entry_frame.pack(fill="x")

        entry = tk.Entry(entry_frame, textvariable=self.split_range_var,
                         font=self.fonts["body"], bg=self.colors["input"],
                         fg="white", insertbackground="white", relief="flat")
        entry.pack(fill="x")

        tk.Label(wrapper, text="Examples: 1-5  or  1,3,5  or  10-end", font=self.fonts["small"],
                 fg=self.colors["subtext"], bg=self.colors["panel"]).pack(anchor="w", pady=5)

    # ================= LOGIC CONNECTORS =================

    def setup_dnd(self):
        try:
            from tkinterdnd2 import DND_FILES
            # If root is DnD compatible
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self.on_drop)
        except:
            pass

    def on_drop(self, event):
        files = self.root.tk.splitlist(event.data)
        self.add_files([f for f in files if f.lower().endswith('.pdf')])

    def browse_files(self):
        files = filedialog.askopenfilenames(filetypes=[("PDF", "*.pdf")])
        if files: self.add_files(files)

    def add_files(self, new_files):
        for f in new_files:
            if f not in self.files and os.path.exists(f):
                self.files.append(f)
        self.refresh_list()

    def refresh_list(self):
        self.listbox.delete(0, tk.END)
        for f in self.files:
            self.listbox.insert(tk.END, f"  📄 {os.path.basename(f)}")
        self.drop_lbl.config(text=f"{len(self.files)} PDF file(s) loaded")

    def clear_list(self):
        self.files = []
        self.refresh_list()

    def move_up(self):
        sel = self.listbox.curselection()
        if not sel or sel[0] == 0: return
        i = sel[0]
        self.files[i], self.files[i - 1] = self.files[i - 1], self.files[i]
        self.refresh_list()
        self.listbox.select_set(i - 1)

    def move_down(self):
        sel = self.listbox.curselection()
        if not sel or sel[0] == len(self.files) - 1: return
        i = sel[0]
        self.files[i], self.files[i + 1] = self.files[i + 1], self.files[i]
        self.refresh_list()
        self.listbox.select_set(i + 1)

    def update_action_button(self, event):
        idx = self.notebook.index(self.notebook.select())
        txt = ["COMPRESS FILES", "MERGE FILES", "EXTRACT PAGES"][idx]
        self.action_btn.config(text=txt)

    def run_process(self):
        if not self.files:
            messagebox.showwarning("No Files", "Please add PDF files first!")
            return

        if not self.gs_path:
            messagebox.showerror("Error", "Ghostscript not found.")
            return

        self.action_btn.config(state="disabled", text="PROCESSING...", bg=self.colors["input"])
        self.progress_frame.pack(fill="x", pady=10)
        self.pbar['value'] = 0

        mode = self.notebook.index(self.notebook.select())
        threading.Thread(target=self.worker, args=(mode,), daemon=True).start()

    def worker(self, mode):
        # 0=Compress, 1=Merge, 2=Split
        successes = 0
        errors = []

        if mode == 1:  # MERGE
            self.p_label.config(text="Merging all files...")
            folder = os.path.dirname(self.files[0])
            name = self.merge_name_var.get().strip() or "merged"
            out = os.path.join(folder, f"{name}.pdf")

            res = merge_pdfs(self.files, out)
            if res["success"]:
                successes = 1
            else:
                errors.append(res["error"])
            self.pbar['value'] = 100

        else:  # BATCH (Compress/Split)
            total = len(self.files)
            for i, f in enumerate(self.files):
                fname = os.path.basename(f)
                self.p_label.config(text=f"Processing: {fname}")
                self.pbar['value'] = (i / total) * 100

                base, ext = os.path.splitext(f)
                if mode == 0:
                    out = f"{base}_compressed{ext}"
                    res = compress_pdf(f, out, self.quality_var.get())
                else:
                    out = f"{base}_extracted{ext}"
                    res = split_pdf(f, out, self.split_range_var.get())

                if res["success"]:
                    successes += 1
                else:
                    errors.append(f"{fname}: {res['error']}")

            self.pbar['value'] = 100

        self.root.after(0, lambda: self.on_complete(successes, errors))

    def on_complete(self, count, errors):
        self.action_btn.config(state="normal", bg=self.colors["primary"])
        self.update_action_button(None)
        self.progress_frame.pack_forget()

        if errors:
            msg = f"Completed with errors.\nSuccess: {count}\n\nErrors:\n" + "\n".join(errors[:3])
            messagebox.showwarning("Finished", msg)
        else:
            if messagebox.askyesno("Success", f"Processed {count} files successfully!\nOpen output folder?"):
                folder = os.path.dirname(self.files[0])
                if sys.platform == 'win32':
                    os.startfile(folder)
                elif sys.platform == 'darwin':
                    subprocess.run(['open', folder])
                else:
                    subprocess.run(['xdg-open', folder])


# ================= MAIN =================

def main():
    # 1. High DPI Support
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except:
        pass

    # 2. Drag & Drop Init
    try:
        from tkinterdnd2 import TkinterDnD
        root = TkinterDnD.Tk()
    except ImportError:
        root = tk.Tk()
        print("Note: Install 'tkinterdnd2' for drag-and-drop support.")

    app = ModernPDFApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()