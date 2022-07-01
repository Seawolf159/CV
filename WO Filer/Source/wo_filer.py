import re
import sys
from configparser import ConfigParser
from pathlib import Path

import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from PyPDF2 import PdfFileReader, PdfFileWriter

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    MAIN_DIR = Path(sys.executable).parent
    FROZEN_DIR = getattr(sys, '_MEIPASS')
else:
    MAIN_DIR = Path(__file__).parent
    FROZEN_DIR = MAIN_DIR


def save_one(chosen_file, progress_signal):
    image_counter = get_pdf_pages(Path(chosen_file), progress_signal)
    save_wo(image_counter, chosen_file, progress_signal)
    remove_leftover_images()


def save_more(chosen_directory, progress_signal):
    for scanned_pdf in Path(chosen_directory).glob("*.pdf"):
        image_counter = get_pdf_pages(scanned_pdf, progress_signal)
        save_wo(image_counter, scanned_pdf, progress_signal)
        remove_leftover_images()


def get_pdf_pages(scanned_pdf, progress_signal):
    progress_signal.emit(1)
    poppler_path = Path(FROZEN_DIR, r"poppler-22.01.0\Library\bin")
    pages = convert_from_path(scanned_pdf,
                              500,
                              poppler_path=poppler_path)

    image_counter = 1
    progress_increment = 50 / len(pages)
    current_progress = 0
    for page in pages:

        # Only save images of the front pages.
        if image_counter % 2 == 0:
            image_counter += 1
            current_progress += progress_increment
            progress_signal.emit(current_progress)
            continue

        filename = Path(FROZEN_DIR, f"page_{image_counter}.jpg")

        page.save(filename, "JPEG")

        image_counter += 1
        current_progress += progress_increment
        progress_signal.emit(current_progress)

    progress_signal.emit(50)
    return image_counter


def save_wo(image_counter, scanned_pdf, progress_signal):
    input_pdf = PdfFileReader(str(scanned_pdf))

    tesseract_path = Path(FROZEN_DIR, r"Tesseract-OCR\tesseract.exe")
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

    wo_num_pattern = re.compile(r"\d\d\d\d30\d\d\d\d")
    current_progress = 50
    progress_increment = 100 / (image_counter)

    for i in range(1, image_counter, 2):
        current_progress += progress_increment
        progress_signal.emit(current_progress)
        filename = Path(FROZEN_DIR, f"page_{i}.jpg")

        text = str(pytesseract.image_to_string(Image.open(filename)))

        try:
            wo_num = wo_num_pattern.search(text).group()
        except AttributeError:
            print(
                "LET OP!! Scan is mogelijk niet goed gegaan of WO Nummer is "
                "moeilijk leesbaar!! Sla de WO van pagina "
                f"{filename.name[5:-4]} & {int(filename.name[5:-4]) + 1} "
                f"handmatig op uit {scanned_pdf}!"
            )
            continue

        try:
            page_1 = input_pdf.getPage(i - 1)
            page_2 = input_pdf.getPage(i)
        except IndexError:
            print("LET OP!! Scan is mogelijk niet goed gegaan!! "
                  "Waarschijnlijk is er niet dubbelzijdig gescant! Scan "
                  f"'{scanned_pdf}' opnieuw en verwijder handmatig eventueel "
                  "verkeerd opgeslagen WO's van de server!")

        pdf_writer = PdfFileWriter()
        pdf_writer.addPage(page_1)
        pdf_writer.addPage(page_2)

        store_location = retrieve_setting("path", "store_location")
        wo_dir_path = Path(store_location, f"{wo_num[:4]}")
        if not wo_dir_path.exists():
            wo_dir_path.mkdir()

        suffix_num = 1
        wo_file_path = Path(wo_dir_path, f"{wo_num}.pdf")
        while wo_file_path.exists():
                suffix_num += 1
                print(
                    f"LET OP!! WO:{wo_num} is al opgeslagen!! "
                    "Mogelijk is deze WO dubbel uitgeprint! Deze WO is nu "
                    "opgeslagen met -[nummer] erachter."
                )
                wo_file_path = Path(wo_dir_path, f"{wo_num}-{suffix_num}.pdf")
        else:
            with wo_file_path.open(mode="wb") as output_file:
                pdf_writer.write(output_file)

    progress_signal.emit(100)


def remove_leftover_images():
    for image in Path(FROZEN_DIR).glob("page*.jpg"):
        Path.unlink(image)


def retrieve_setting(section, option):
    settings = ConfigParser()
    settings.read(Path(MAIN_DIR, "settings.ini"))

    return settings[section][option]


def store_setting(section, option, value):
    settings = ConfigParser()
    settings.read(Path(MAIN_DIR, "settings.ini"))
    settings[section][option] = value

    with open(Path(MAIN_DIR, "settings.ini"), 'w') as f:
        settings.write(f)
