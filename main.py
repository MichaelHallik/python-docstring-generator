"""
A web-based application built with NiceGUI to generate Python docstrings
in Google, reStructuredText (reST), or NumPy style.

Features:

- UI inputs for summary, description, arguments, return values, and exceptions.
- Dynamic formatting and line wrapping according to selected style.
- Responsive, centered interface.
- Docstring output wrapped in triple quotes.
- One-click copy functionality.

This application allows users to interactively create Python function 
docstrings in one of three supported styles:

Google, reStructuredText (reST), or NumPy.

Users can input summary and extended descriptions, and specify function
arguments, return values, and raised exceptions. The resulting docstring 
is rendered in the selected format with a configurable line length and 
presented in a readonly text area.

Features:
---------
- Clean, responsive UI using NiceGUI and Tailwind classes.
- Support for Google, reST, and NumPy docstring formats.
- User inputs for:
  * Summary line
  * Extended description
  * Dynamic lists of Args, Returns, and Raises
- Selectable maximum line length with word wrapping.
- Preserves line breaks and indentation in multi-line text.
- Fully formatted docstring wrapped in triple quotes.
- One-click copy to clipboard.

Structure:
----------
- DocstringGenerator() class manages state, layout, and formatting logic.
- Helper methods:
  * `add_entry()` — add name/description input pairs.
  * `create_section()` — build form blocks for inputs.
  * `wrap_text()` — paragraph-wise text wrapping with indentation.
  * `generate_docstring()` — constructs and formats the final docstring.
  * `build_ui()` — defines and renders the user interface.

Run:
-----
Execute the script to start the NiceGUI server.

The interface will be available in a browser window at 
`http://localhost:8080`.

Requirements:
-------------
- Python 3.8+
- nicegui (install via `pip install nicegui`)

"""


from typing import List, Tuple
import textwrap
from nicegui import ui


STYLE_DEFAULTS = {
    "reStructuredText (reST)": 79,
    "Google Style": 100,
    "NumPy Style": 100,
    }


class DocstringSection:
    """
    Represents a dynamic input section for a specific docstring 
    component (e.g. Args).

    Manages the UI card, associated input fields, and stored data.
    """
    def __init__(self, label: str):
        self.label = label
        self.entries: List[Tuple] = []
        self.container = None

    def create_ui(self):
        """
        Create the UI section as a card with add-entry button.
        """
        with ui.card().classes("mb-4 w-full"):
            ui.label(self.label)
            self.container = ui.column().classes("w-full")
            ui.button(f"Add {self.label}", on_click=self.add_entry)

    def add_entry(self):
        """
        Add a new name/description input pair to this section.
        """
        with self.container: # type: ignore
            with ui.row().classes("gap-2 w-full"):
                name_input = ui.input("Name").classes("w-1/4")
                desc_input = ui.textarea("Description").classes("w-3/4")
                self.entries.append((name_input, desc_input))

    def collect_data(self) -> List[Tuple[str, str]]:
        """
        Return a list of (name, description) values from UI inputs.
        """
        return [
            (name.value, desc.value)
            for name, desc in self.entries
            if name.value or desc.value
        ]

class DocstringFormatter:
    """
    Handles the generation and formatting of docstrings.

    Accepts structured inputs and produces a formatted string output.
    """
    def __init__(self):
        self.max_len = STYLE_DEFAULTS["Google Style"]

    def wrap_text(self, text: str, indent: int = 8) -> str:
        """
        Wrap text with the given indentation and max line length.
        """
        pad = " " * indent
        paragraphs = text.split('\n')
        wrapped = []
        for para in paragraphs:
            if para.strip():
                wrapped.append("\n".join(
                    textwrap.wrap(
                        para,
                        width=self.max_len - indent,
                        initial_indent=pad,
                        subsequent_indent=pad,
                    )
                ))
            else:
                wrapped.append("")
        return "\n".join(wrapped)

    def generate( # pylint: disable=R0913:too-many-arguments disable=R0917:too-many-positional-arguments disable=R0912:too-many-branches
        self,
        style: str,
        summary: str,
        description: str,
        args: List[Tuple[str, str]],
        returns: List[Tuple[str, str]],
        raises: List[Tuple[str, str]]) -> str:
        """
        Construct a docstring in the specified format using the provided 
        content.

        Args:
            style:
                Selected docstring format (Google, reST, NumPy).
            summary:
                Short one-line summary.
            description:
                Extended multi-line description.
            args:
                List of argument name/description pairs.
            returns:
                List of return value descriptions.
            raises:
                List of raised exceptions and their explanations.

        Returns:
            A complete docstring wrapped in triple quotes.
        """
        body = ""
        if style == "Google Style":
            if args:
                body += "Args:\n"
                for name, desc in args:
                    body += f"    {name}:\n{self.wrap_text(desc)}\n"
            if returns:
                body += "\nReturns:\n"
                for name, desc in returns:
                    body += f"    {name}:\n{self.wrap_text(desc)}\n"
            if raises:
                body += "\nRaises:\n"
                for name, desc in raises:
                    body += f"    {name}:\n{self.wrap_text(desc)}\n"
        elif style == "reStructuredText (reST)":
            for name, desc in args:
                body += f":param {name}:\n{self.wrap_text(desc)}\n"
            for name, desc in returns:
                body += f":return {name}:\n{self.wrap_text(desc)}\n"
            for name, desc in raises:
                body += f":raises {name}:\n{self.wrap_text(desc)}\n"
        elif style == "NumPy Style":
            if args:
                body += "Parameters\n----------\n"
                for name, desc in args:
                    body += f"{name} :\n{self.wrap_text(desc, indent=4)}\n"
            if returns:
                body += "\nReturns\n-------\n"
                for name, desc in returns:
                    body += f"{name} :\n{self.wrap_text(desc, indent=4)}\n"
            if raises:
                body += "\nRaises\n------\n"
                for name, desc in raises:
                    body += f"{name} :\n{self.wrap_text(desc, indent=4)}\n"
        # Assemble the full docstring.
        parts = ['"""']
        if summary:
            parts.append(self.wrap_text(summary, indent=0))
        if description:
            parts.append("\n" + self.wrap_text(description, indent=0))
        if body.strip():
            parts.append("\n" + body.strip())
        parts.append('"""')
        return "\n\n".join(parts)

class DocstringUI: # pylint: disable=R0902:too-many-instance-attributes
    """
    The main UI controller that integrates user inputs, layout, and 
    formatting.

    Manages interaction between form controls and the docstring formatter.
    """
    def __init__(self):
        self.summary_input = None
        self.description_input = None
        self.format_dropdown = None
        self.line_length_dropdown = None
        self.output_area = None
        self.args = DocstringSection("Args")
        self.returns = DocstringSection("Returns")
        self.raises = DocstringSection("Raises")
        self.formatter = DocstringFormatter()

    def build(self):
        """
        Construct the complete UI layout.
        """
        with ui.column().classes(
            'w-full max-w-4xl mx-auto p-4 gap-4'
            ):
            ui.label(
                "Python Docstring Generator"
                ).classes("text-2xl font-bold mb-4")
            self.summary_input = ui.input(
                "Summary line (one-liner)"
                ).classes("w-full")
            self.description_input = ui.textarea(
                "Extended description (optional)"
                ).classes("w-full h-24")
            self.args.create_ui()
            self.returns.create_ui()
            self.raises.create_ui()
            with ui.row().classes("gap-4 w-full"):
                self.format_dropdown = ui.select(
                    list(STYLE_DEFAULTS.keys()),
                    value="Google Style",
                    label="Format/style",
                    )
                self.line_length_dropdown = ui.select(
                    ["default", "72", "79", "88", "100", "120"],
                    value="default",
                    label="Max line length",
                    )
            ui.button(
                "Create docstring", on_click=self.generate
                ).classes("mt-4")
            self.output_area = ui.textarea(
                label="Generated Docstring"
                ).classes("w-full h-80 mt-4 font-mono")
            self.output_area.props('readonly')
            ui.button(
                "Copy to Clipboard", on_click=lambda: ui.run_javascript(
                    f"navigator.clipboard.writeText(`{self.output_area.value}`)" # type: ignore
                    )
                )

    def generate(self):
        """
        Callback that collects data and triggers docstring generation.
        """
        style = self.format_dropdown.value or "Google Style" # type: ignore
        line_setting = self.line_length_dropdown.value or "default" # type: ignore
        self.formatter.max_len = (
            int(line_setting)
            if line_setting != "default"
            else STYLE_DEFAULTS[style]
        )
        result = self.formatter.generate(
            style,
            self.summary_input.value or "", # type: ignore
            self.description_input.value or "", # type: ignore
            self.args.collect_data(),
            self.returns.collect_data(),
            self.raises.collect_data(),
        )
        self.output_area.value = result # type: ignore

# Run the app.
app = DocstringUI()
app.build()

if __name__ in ['__main__', '__mp_main__']:
    ui.run()
