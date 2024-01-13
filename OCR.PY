import os
from pdfminer.high_level import extract_text
import pytesseract
from PIL import Image
from pdf2image import convert_from_path

def extract_content(file_path):
    # Check the file extension
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()

    if file_extension in ['.pdf']:
        # Extract text from PDF
        text = extract_text(file_path)

        # Convert PDF pages to images and extract text from images
        images = convert_from_path(file_path)
        for image in images:
            text += pytesseract.image_to_string(image)

        return text

    elif file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
        # Extract text from an image file
        text = pytesseract.image_to_string(Image.open(file_path))
        return text

    else:
        raise ValueError("Unsupported file type")

# Example usage
file_path = '/Users/trams/Downloads/ocr pdf/CP_RING5_11172023.pdf'  # or an image file
extracted_content = extract_content(file_path)
print(extracted_content)