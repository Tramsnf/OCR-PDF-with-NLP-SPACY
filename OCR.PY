import sys
from pdfminer.high_level import extract_text
import os
from PIL import Image
import pytesseract
import cv2
import pdf2image
import pandas as pd
import numpy as np
import concurrent.futures



def is_scanned_pdf(pdf_path):
    """Check if a PDF is image-based (scanned) or contains selectable text."""
    try:
        # Extract the first page text
        first_page_text = extract_text(pdf_path, page_numbers=[0])
        # If the extracted text is empty or very short, it's likely a scanned PDF
        return len(first_page_text.strip()) < 50
    except Exception:
        # In case of any error, assume it's scanned to proceed with OCR
        return True


def extract_text_from_pdf_with_page_numbers(pdf_path):
    """Extracts text from a text-based PDF file with page numbers."""
    text_by_page = []
    for page_num, page_layout in enumerate(pdf2image.convert_from_path(pdf_path)):
        page_text = extract_text(pdf_path, page_numbers=[page_num])
        text_by_page.append(f"--- Page {page_num + 1} ---\n{page_text}")
    return '\n'.join(text_by_page)

def convert_pdf_to_images(pdf_path):
    """Converts each page of the PDF into an image."""
    return pdf2image.convert_from_path(pdf_path)


def preprocess_image_for_ocr(image):
    """Preprocesses the image to improve OCR accuracy."""
    # Convert to grayscale
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
    # Apply thresholding
    _, thresh = cv2.threshold(
        gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return Image.fromarray(thresh)


def extract_text_from_image(image):
    """Extracts text from an image using Tesseract OCR."""
    preprocessed_image = preprocess_image_for_ocr(image)
    text = pytesseract.image_to_string(preprocessed_image)
    return text


def extract_text_from_scanned_pdf_with_page_numbers(pdf_path):
    """Extracts text from a scanned PDF file with page numbers."""
    images = convert_pdf_to_images(pdf_path)
    all_text = []
    for page_num, image in enumerate(images):
        text = extract_text_from_image(image)
        all_text.append(f"--- Page {page_num + 1} ---\n{text}")
    return '\n'.join(all_text)


def main():
    file_path = '/Users/trams/Downloads/ocr pdf/CP_RING5_11172023.pdf'
    # input_path = sys.argv[1]  # Get file path from command line argument

    if not os.path.exists(file_path):
        print("File not found.")
        return

    file_extension = os.path.splitext(file_path)[1].lower()

    if file_extension in ['.pdf']:
        if is_scanned_pdf(file_path):
            print("Extracting text from scanned PDF...")
            text = extract_text_from_scanned_pdf_with_page_numbers(file_path)
            print("Extracted Text:\n", text)
        else:
            print("Extracting text from text-based PDF...")
            text = extract_text_from_scanned_pdf_with_page_numbers(file_path)
        print("Extracted Text:\n", text)

    elif file_extension in ['.jpg', '.jpeg', '.png', '.tiff']:
        print("Extracting text from image...")
        image = Image.open(file_path)
        text = extract_text_from_image(image)
        print("Extracted Text:\n", text)

    else:
        print("Unsupported file type.")


if __name__ == "__main__":
    main()
