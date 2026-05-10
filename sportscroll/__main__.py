"""Entry point for SportScroll.

Fetches event data and renders it to a dated PDF in output/.
"""

# Standard library Imports
from datetime import datetime

# Related third party imports

# Local application/library specific imports
from sportscroll.config import get_timezone
from sportscroll.data import get_pdf_data
from sportscroll.pdf import generate_pdf



def main():
    """Fetches event data and renders it to a PDF."""
    run_date = datetime.now(get_timezone())
    data = get_pdf_data(target_date=run_date)
    generate_pdf(pdf_data=data, target_date=run_date)

if __name__ == "__main__":
    main()
