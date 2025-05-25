# Python docstring generator

This repository contains a NiceGUI-based web application that allows developers to generate Python docstrings in three popular formats:

Google, reStructuredText (reST), and NumPy

## Features

- Dynamic web form for entering:
  - One-line summary.
  - Extended description.
  - Arguments.
  - Return values.
  - Raised exceptions.
- Style selection: Google, reST, NumPy.
- Line wrapping based on selectable max length (e.g. 79, 100, 120 chars).
- Responsive and centered UI layout using Tailwind CSS.
- Read-only output with one-click clipboard copy.
- All user input preserved as written (line breaks, indentation).

## Screenshot

![Screenshot of the app](web_ui.JPG)

## Installation

```bash
pip install nicegui
git clone https://github.com/yourname/docstring-generator.git
cd docstring-generator
python main.py
```

Then visit [http://localhost:8080](http://localhost:8080) in your browser.

## Requirements

- Python 3.8 or higher
- [NiceGUI](https://github.com/zauberzeug/nicegui)

## Why use this?

Writing structured and standards-compliant docstrings by hand can be tedious.

This tool simplifies that by guiding you through each section and taking care of the formatting.

## Project structure

```text
main.py          # Entry point for the app with UI, formatting, and logic
README.md        # Project documentation and usage
TECHNICAL.md     # Technical implementation details and architecture
```

## 🪪 License

MIT License