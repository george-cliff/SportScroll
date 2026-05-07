from src.data import get_pdf_data
from src.pdf import generate_pdf

def main():
    data = get_pdf_data() # fetches the data
    generate_pdf(pdf_data=data) # renders the data


if __name__ == "__main__":
    main()