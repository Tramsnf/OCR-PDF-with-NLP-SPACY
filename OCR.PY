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
import logging
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def safe_execute(function):
    """Decorator for safe execution with logging."""
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {function.__name__}: {e}")
            return None
    return wrapper


@safe_execute
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


@safe_execute
def extract_text_from_pdf_with_page_numbers(pdf_path):
    """Extracts text from a text-based PDF file with page numbers."""
    text_by_page = []
    for page_num, page_layout in enumerate(pdf2image.convert_from_path(pdf_path)):
        page_text = extract_text(pdf_path, page_numbers=[page_num])
        text_by_page.append(f"--- Page {page_num + 1} ---\n{page_text}")
    return '\n'.join(text_by_page)


@safe_execute
def convert_pdf_to_images(pdf_path):
    """Converts each page of the PDF into an image, optimized for large PDFs."""
    try:
        # Increased DPI
        return pdf2image.convert_from_path(pdf_path, thread_count=5, dpi=300)
    except Exception as e:
        logging.error(f"Error converting PDF to images: {e}")
        return []


# @safe_execute
# def apply_dilation_erosion(image):
#     kernel = np.ones((1, 1), np.uint8)
#     image = cv2.dilate(image, kernel, iterations=1)
#     image = cv2.erode(image, kernel, iterations=1)
#     return image


# @safe_execute
# def correct_skew(image):
#     coords = np.column_stack(np.where(image > 0))
#     angle = cv2.minAreaRect(coords)[-1]
#     if angle < -45:
#         angle = -(90 + angle)
#     else:
#         angle = -angle
#     (h, w) = image.shape[:2]
#     center = (w // 2, h // 2)
#     M = cv2.getRotationMatrix2D(center, angle, 1.0)
#     image = cv2.warpAffine(image, M, (w, h),
#                            flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
#     return image

# @safe_execute
# def preprocess_image_for_ocr(image):
#     """Preprocesses the image with enhancement techniques for better OCR results."""
#     # Convert to grayscale
#     gray = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
#     # Apply noise reduction
#     denoised = cv2.fastNlMeansDenoising(gray, h=10)
#     # Apply thresholding
#     _, thresh = cv2.threshold(
#         denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
#     # corrected = correct_skew(thresh)
#     # final_image = apply_dilation_erosion(corrected)
#     # return Image.fromarray(final_image)
#     return Image.fromarray(thresh)


@safe_execute
def preprocess_image_for_ocr(image):
    """Preprocesses the image with enhancement techniques for better OCR results."""
    # Convert PIL Image to a NumPy array
    image_np = np.array(image)

    # Apply noise reduction for color images
    denoised = cv2.fastNlMeansDenoisingColored(image_np, None, 10, 10, 7, 21)

    # Convert back to PIL Image and return
    return Image.fromarray(denoised)


@safe_execute
def extract_text_from_image(image):
    # """Extracts text from an image using Tesseract OCR."""
    # preprocessed_image = preprocess_image_for_ocr(image)
    # text = pytesseract.image_to_string(preprocessed_image)
    # return text

    """Extracts text from an image using Tesseract OCR with enhanced settings."""
    preprocessed_image = preprocess_image_for_ocr(image)
    custom_config = r'--oem 3 --psm 1'  # Experiment with different configurations
    text = pytesseract.image_to_string(
        preprocessed_image, config=custom_config)
    return text


@safe_execute
def extract_text_from_scanned_pdf_with_page_numbers(pdf_path):
    """Extracts text from a scanned PDF file with page numbers."""
    images = convert_pdf_to_images(pdf_path)
    all_text = []
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(extract_text_from_image, image)
                   for image in images]
        for page_num, future in enumerate(futures):
            text = future.result()
            all_text.append(f"--- Page {page_num + 1} ---\n{text}")

    return '\n'.join(all_text)


@safe_execute
def main():
    file_path = '/Users/trams/Downloads/ocr pdf/CP_RING5_11172023.pdf'
    # file_path = '/Users/trams/Downloads/ocr pdf/IFA REV1.pdf'
    # file_path = '/Users/trams/Pictures/Scan 5.jpeg'
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
            text = extract_text_from_pdf_with_page_numbers(file_path)
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






# import sys
# from pdfminer.high_level import extract_text
# import os
# from PIL import Image
# import pytesseract
# import cv2
# import pdf2image
# import pandas as pd
# import numpy as np
# import concurrent.futures



# def is_scanned_pdf(pdf_path):
#     """Check if a PDF is image-based (scanned) or contains selectable text."""
#     try:
#         # Extract the first page text
#         first_page_text = extract_text(pdf_path, page_numbers=[0])
#         # If the extracted text is empty or very short, it's likely a scanned PDF
#         return len(first_page_text.strip()) < 50
#     except Exception:
#         # In case of any error, assume it's scanned to proceed with OCR
#         return True


# def extract_text_from_pdf_with_page_numbers(pdf_path):
#     """Extracts text from a text-based PDF file with page numbers."""
#     text_by_page = []
#     for page_num, page_layout in enumerate(pdf2image.convert_from_path(pdf_path)):
#         page_text = extract_text(pdf_path, page_numbers=[page_num])
#         text_by_page.append(f"--- Page {page_num + 1} ---\n{page_text}")
#     return '\n'.join(text_by_page)

# def convert_pdf_to_images(pdf_path):
#     """Converts each page of the PDF into an image."""
#     return pdf2image.convert_from_path(pdf_path)


# def preprocess_image_for_ocr(image):
#     """Preprocesses the image to improve OCR accuracy."""
#     # Convert to grayscale
#     gray = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
#     # Apply thresholding
#     _, thresh = cv2.threshold(
#         gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
#     return Image.fromarray(thresh)


# def extract_text_from_image(image):
#     """Extracts text from an image using Tesseract OCR."""
#     preprocessed_image = preprocess_image_for_ocr(image)
#     text = pytesseract.image_to_string(preprocessed_image)
#     return text


# def extract_text_from_scanned_pdf_with_page_numbers(pdf_path):
#     """Extracts text from a scanned PDF file with page numbers."""
#     images = convert_pdf_to_images(pdf_path)
#     all_text = []
#     for page_num, image in enumerate(images):
#         text = extract_text_from_image(image)
#         all_text.append(f"--- Page {page_num + 1} ---\n{text}")
#     return '\n'.join(all_text)


# def main():
#     file_path = '/Users/trams/Downloads/ocr pdf/CP_RING5_11172023.pdf'
#     # input_path = sys.argv[1]  # Get file path from command line argument

#     if not os.path.exists(file_path):
#         print("File not found.")
#         return

#     file_extension = os.path.splitext(file_path)[1].lower()

#     if file_extension in ['.pdf']:
#         if is_scanned_pdf(file_path):
#             print("Extracting text from scanned PDF...")
#             text = extract_text_from_scanned_pdf_with_page_numbers(file_path)
#             print("Extracted Text:\n", text)
#         else:
#             print("Extracting text from text-based PDF...")
#             text = extract_text_from_scanned_pdf_with_page_numbers(file_path)
#         print("Extracted Text:\n", text)

#     elif file_extension in ['.jpg', '.jpeg', '.png', '.tiff']:
#         print("Extracting text from image...")
#         image = Image.open(file_path)
#         text = extract_text_from_image(image)
#         print("Extracted Text:\n", text)

#     else:
#         print("Unsupported file type.")


# if __name__ == "__main__":
#     main()
