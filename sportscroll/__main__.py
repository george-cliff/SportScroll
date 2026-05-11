"""Entry point for SportScroll.

Fetches event data and renders it to a dated PDF in output/.
"""

# Standard library Imports
import logging
import sys
from datetime import datetime

# Related third party imports

# Local application/library specific imports
from sportscroll.config import get_timezone
from sportscroll.data import get_pdf_data
from sportscroll.pdf import generate_pdf

logger = logging.getLogger(__name__)


def main():
    """Fetches event data and renders it to a PDF."""
    # Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
    )
    logger.info("SportScroll run started")
    try:
        run_date = datetime.now(get_timezone())
        data = get_pdf_data(target_date=run_date)
        generate_pdf(pdf_data=data, target_date=run_date)
    except Exception:
        logger.exception("Run failed")
        sys.exit(1)
    logger.info("SportScroll run finished")


if __name__ == "__main__":
    main()
