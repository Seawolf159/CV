import sys
from configparser import ConfigParser
from pathlib import Path

import openpyxl

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    MAIN_DIR = Path(sys.executable).parent
else:
    MAIN_DIR = Path(__file__).parent


def create_and_save_labels(progress_signal):
    products = get_sap_data()
    template_text = get_template_text()
    template_long_name_text = get_template_long_name_text()

    progress_increment = 100 / len(products)
    progress = 0
    directory = load_setting("path", "label_location")
    for product in products:
        new_label_text = replace_template_text(
            product, template_text, template_long_name_text
        )

        file_name = f"{product[0]:04d}.label"
        label_path = Path(directory, file_name)
        save_new_label(label_path, new_label_text)

        progress += progress_increment
        progress_signal.emit(progress)


def get_sap_data():
    excel_path = Path(load_setting("path", "excel"))

    workbook = openpyxl.load_workbook(excel_path)

    sap_data_sheet = workbook.active
    sap_data = sap_data_sheet.tables["ProductTable"]
    sap_data_range = sap_data_sheet[sap_data.ref]

    products = [
        [cell.value for cell in row] for row in sap_data_range[1:]
    ]

    return products


def get_template_text():
    path = Path(load_setting("path", "short_template"))
    with open(path, 'r') as f:
        template_text = f.read()
        return template_text


def get_template_long_name_text():
    path = Path(load_setting("path", "long_template"))
    with open(path, 'r') as f:
        template_text = f.read()
        return template_text


def replace_template_text(product,
                          template_text,
                          template_long_name_text):
    pr_num = product[0]
    description = product[1]

    # Always replace '&' with '&amp;' or the label gives an error.
    if '&' in description:
        description = description.replace("&", "&amp;")

    # Check how long the description is to determine which template text
    # to use.
    max_len = 35
    if len(description) > max_len:
        first_part = []
        second_part = []
        description = description.split()
        while description:
            part = description.pop(0)
            if len(' '.join(first_part)) > max_len:
                second_part.append(part)
            else:
                first_part.append(part)

        if not second_part:
            new_label_text = template_text.replace(
                "{0000}", f"{pr_num:04d}"
            )
        else:
            new_label_text = template_long_name_text.replace(
                "{0000}", f"{pr_num:04d}"
            )

            new_label_text = new_label_text.replace(
                "{Continuation of Product description}",
                ' '.join(second_part)
            )

        new_label_text = new_label_text.replace(
            "{Product description}", ' '.join(first_part)
        )
    else:
        new_label_text = template_text.replace("{0000}", f"{pr_num:04d}")
        new_label_text = new_label_text.replace(
            "{Product description}", description
        )
    return new_label_text


def save_new_label(label_path, text):
    with open(label_path, 'w') as f:
        f.write(text)


def load_setting(section, option):
    settings = ConfigParser()
    settings.read(Path(MAIN_DIR, "settings.ini"))

    return settings[section][option]


def save_setting(section, option, value):
    settings = ConfigParser()
    settings.read(Path(MAIN_DIR, "settings.ini"))
    settings[section][option] = value

    with open(Path(MAIN_DIR, "settings.ini"), 'w') as f:
        settings.write(f)
