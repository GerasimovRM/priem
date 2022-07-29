import csv
import json


def format_phone(phone_number: str) -> str:
    phone_number = phone_number.replace("(", "").replace(")", "").replace("-", "")
    if phone_number.startswith("8"):
        phone_number = "+7" + phone_number[1:]
    phone_number = "-".join([phone_number[:2], phone_number[2:5], phone_number[5:8], phone_number[8:10], phone_number[10:12]])
    return phone_number


with open("уник2.csv", newline="", encoding="utf8") as csv_file:
    reader = csv.reader(csv_file, delimiter=";")
    data = sorted(set(map(tuple, filter(lambda x: "" not in x and "ФИО" not in x, reader))),
                  key=lambda t: t[0])
    data = list(map(lambda x: (" ".join(map(str.capitalize, x[0].split())),) + (x[1:]), data))
    data = list(map(lambda x: x[:1] + ("\n".join(map(lambda p: format_phone(p), x[1].split("; "))),) + x[2:], data))
    data = {x[-1]: x[:-1] for x in data}

with open("students.json", "w", encoding="utf8") as json_result:
    json.dump(data, json_result)
