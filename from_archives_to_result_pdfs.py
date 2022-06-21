import PIL.Image

from settings import DATA_DIR, ZIP_DIR
import zipfile
import os
import img2pdf
import glob
from PyPDF2 import PdfFileMerger
from io import BytesIO
import shutil


def images_to_pdf_file(images_names, dst_dir_path, pdf_name, not_taken_files=None):
    if not pdf_name.endswith(".pdf"):
        pdf_name += ".pdf"

    images_bytes = []
    for image_name in images_names:
        raw_data = open(image_name, "rb").read()
        try:
            PIL.Image.open(BytesIO(raw_data))
            images_bytes.append(raw_data)
        except PIL.UnidentifiedImageError:
            not_taken_files.append(image_name)
    if images_bytes:
        with open(dst_dir_path + "\\" + pdf_name, "wb") as f:
            f.write(img2pdf.convert(images_bytes))

"""
def join_pdf_files_from_dir(pdfs_dir_path, dst_dir_path=None):
    if not dst_dir_path:
        dst_dir_path = pdfs_dir_path
    dir_name = pdfs_dir_path.split("\\")[-1]
    pdfs = glob.glob(f"{pdfs_dir_path}\\*.pdf")
    join_pdf_files(pdfs, dst_dir_path, dir_name)
"""


def join_pdf_files(pdf_files_paths, dst_dir_path, pdf_name, not_taken_files=None):
    if not pdf_name.endswith(".pdf"):
        pdf_name += ".pdf"

    merger = PdfFileMerger()
    for pdf in pdf_files_paths:
        try:
            merger.append(pdf)
        except Exception as e:
            print(e)
            if not_taken_files:
                not_taken_files.append(pdf)
    merger.write(f"{dst_dir_path}\\{pdf_name}")
    merger.close()


def get_files_by_extension(files, extension):
    return list(filter(lambda file: file.endswith(extension), files))


def zip_to_dir(zip_path):
    zip_name = zip_path.split("\\")[-1].split(".")[0]
    dst = DATA_DIR + f"\\{zip_name}"
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(dst)


if not os.path.exists("data"):
    os.makedirs("data")

if not os.path.exists("RESULT"):
    os.makedirs("RESULT")

zip_names = glob.glob(f"{ZIP_DIR}\\*.zip")
for zip_name in filter(lambda x: x.endswith(").zip"), zip_names):
    os.remove(zip_name)

zip_names = glob.glob(f"{ZIP_DIR}\\*.zip")
for zip_name in zip_names:
    zip_to_dir(zip_name)

# pngs to jpgs and delete pngs
for student_name in next(os.walk("data"))[1]:
    for root, dirs, files in list(os.walk(f"data\\{student_name}"))[::-1]:
        files = files[::-1]  # костыль, чтобы паспорт был впереди
        pngs_in_current_dir = list(map(lambda x: root + "\\" + x,
                                       get_files_by_extension(files, ".png")))
        for png_in_current_dir in pngs_in_current_dir:
            image = PIL.Image.open(png_in_current_dir).convert("RGB")
            image_jpg_name = png_in_current_dir.rsplit(".", 1)[0] + ".jpg"
            image.save(image_jpg_name)
            os.remove(png_in_current_dir)

for student_name in next(os.walk("data"))[1]:
    not_taken_files = []
    for root, dirs, files in list(os.walk(f"data\\{student_name}"))[::-1]:
        # print(root, dirs, files)
        current_dir_name = root.split("\\")[-1]
        # jpgs from folder to one pdf
        pdfs_in_current_dir = get_files_by_extension(files, ".pdf")
        jpgs_in_current_dir = get_files_by_extension(files, ".jpg")
        if jpgs_in_current_dir:
            full_jpgs = list(map(lambda jpg: root + "\\" + jpg, jpgs_in_current_dir))
            images_to_pdf_file(full_jpgs, root, "jpgs", not_taken_files)
        # find not taken files
        sub_not_taken_files = set(files) - (set(pdfs_in_current_dir) | set(jpgs_in_current_dir))
        if sub_not_taken_files:
            not_taken_files.extend(map(lambda x: root + "\\" + x, sub_not_taken_files))
        # find pdfs for join from child folders
        pdfs_from_extension_dirs = glob.glob(f"{root}\\**\\*_sub.pdf")
        pdfs_to_add_current_dir = list(map(lambda pdf: root + "\\" + pdf, filter(lambda x: not x.endswith("_sub.pdf"),
                                                                                 pdfs_in_current_dir))) + pdfs_from_extension_dirs
        # join pdfs from child folders
        if pdfs_to_add_current_dir:
            join_pdf_files(pdfs_to_add_current_dir, root, current_dir_name + "_sub", not_taken_files)

    # find jpgs and pdfs for join and join to RESULT_<student_name>.pdf
    result_files = []
    result_files.extend(glob.glob(f"data\\{student_name}\\jpgs.pdf"))
    result_files.extend(glob.glob(f"data\\{student_name}\\{student_name}_sub.pdf"))
    join_pdf_files(result_files, root, f"RESULT_{student_name}")
    # log to console bad documents
    if not_taken_files:
        print("=" * 20)
        print(f"{student_name} not taken files:")
        print(*not_taken_files, sep='\n')
        print("=" * 20)
    not_taken_files.clear()

# copy from folders to result FOLDER
results_files = glob.glob("data\\*\\RESULT_*.pdf")
for result_file in results_files:
    result_file_in_result_directory = "RESULT\\" + result_file.split("\\")[-1]
    if os.path.isfile(result_file_in_result_directory):
        os.remove(result_file_in_result_directory)
    shutil.copy(result_file, "RESULT\\")

# delete all sub files
jpgs_for_remove = glob.glob("data\\**\\jpgs.pdf", recursive=True)
pdfs_for_remove = glob.glob("data\\**\\*_sub.pdf", recursive=True)
result_pdfs_for_remove = glob.glob("data\\**\\RESULT_*.pdf", recursive=True)
for file_for_remove in jpgs_for_remove + pdfs_for_remove + result_pdfs_for_remove:
    os.remove(file_for_remove)





