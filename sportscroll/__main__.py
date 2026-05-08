"""Entry point for SportScroll.

Fetches event data and renders it to a dated PDF in output/.
"""

# Standard library Imports

# Related third party imports

# Local application/library specific imports
from sportscroll.data import get_pdf_data
from sportscroll.pdf import generate_pdf


def main():
    """Fetches event data and renders it to a PDF."""
    data = get_pdf_data()
    generate_pdf(pdf_data=data)


if __name__ == "__main__":
    main()
