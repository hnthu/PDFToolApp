# PDF Toolkit - Modern UI Edition

A clean, modern, flat-UI desktop application for managing PDF files. Built with Python and Tkinter, featuring a dark mode interface and Drag & Drop support.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-yellow.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS-lightgrey.svg)

## 🌟 Features

* **Clean Dark UI:** Modern flat design with large typography.
* **Drag & Drop:** Easily drag PDF files directly into the application.
* **Compress:** Reduce file size with 3 quality presets (Screen, eBook, Printer).
* **Merge:** Combine multiple PDFs into a single document.
* **Split:** Extract specific pages or ranges (e.g., `1-5`, `10-end`).
* **Robust Backend:** Uses Ghostscript for reliable PDF processing.

## 🛠 Prerequisites

This application relies on **Ghostscript** for PDF processing.

### Windows
1.  Download and install Ghostscript (AGPL Release) from the [official website](https://www.ghostscript.com/releases/gsdnld.html).
2.  Ensure the installer adds Ghostscript to your system PATH (usually selected by default).

### macOS
Install via Homebrew:
```bash
brew install ghostscript