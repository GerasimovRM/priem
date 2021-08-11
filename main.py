from from_site_to_archives import FromCiteToArchive


parser = FromCiteToArchive("config.ini")

with open("students.txt", encoding="utf-8") as students_file:
    for student_fio in map(str.strip, students_file.readlines()):
        parser.find_person_and_load_data(student_fio)
parser.close()