from os.path import exists
from pprint import pprint

import requests

from from_site_to_archives import FromCiteToArchive

parser = FromCiteToArchive("config.ini")

"""
# run abiturients.server
abiturients_with_original_and_agreement = requests.get("http://127.0.0.1:5000/get_agreement_with_original_docs").json()
# pprint(abiturients_with_original_and_agreement)

zip_dir = parser.zip_dir
for direction in abiturients_with_original_and_agreement:
    print(direction, "=" * 10)
    for abiturient in abiturients_with_original_and_agreement[direction]:
        if exists(f"{zip_dir}\\{direction}\\{abiturient['ФИО'].replace(' ', '_')}.zip"):
            print(abiturient['ФИО'], "уже скачан!")
        else:
            parser.find_person_and_load_data(abiturient["ФИО"], direction)
parser.close_all_webdrivers()
"""



#
import from_archives_to_result_pdfs
