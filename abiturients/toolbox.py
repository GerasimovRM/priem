import urllib.request
from urllib.parse import quote

import pandas as pd
from bs4 import BeautifulSoup
from mongo_client import DbClient

import json

import logging


def get_json(url, name, db):
    print(url, name)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    tml = urllib.request.urlopen(req).read()
    tables = pd.read_html(tml, header=12)
    x = tables[0].drop(columns=tables[0].columns[12])
    x = x.drop(columns=x.columns[12])

    file_name = 'json/' + name + '.json'

    with open(file_name, 'w', encoding='UTF-8') as file:
        x.to_json(file, force_ascii=False, orient='table')

    with open(file_name, encoding="utf8") as f:
        data = json.load(f)
        for i in data['data']:
            i["_id"] = i.pop("Уникальный код")
            i["Рейтинг"] = i.pop("Номер ПП")
            i["Математика"] = i.pop("Математика уровень СПО / Математика")

            try:
                i["Информатика/Физика"] = i.pop(
                    "Информатика и ИКТ уровень СПО / Физика уровень СПО / Информатика и ИКТ / Физика")
            except:
                i["Физика"] = i.pop("Физика уровень СПО / Физика")
            i["Русский язык"] = i.pop("Русский язык")
            i['Сумма баллов за инд.дост.(конкурсные)'] = i.pop("Сумма баллов за инд.дост.(конкурсные)")
            i['Сумма баллов'] = i.pop("Сумма баллов")
            i['Преимущ.право'] = i.pop('Преимущ.право')
            i['Вид документа об образовании'] = i.pop('Вид документа об образовании')
            i['Согласие на зачисление'] = i.pop('Согласие на зачисление')
            # i['Есть согласие на другое направление'] = i.pop('Есть согласие на другое направление')
            i['Подтверждающий документ (целевого направления)'] = i.pop(
                'Подтверждающий документ (целевого направления)')
            i['Доставка документов'] = i.pop('Доставка документов')

    with open(file_name, 'w', encoding='utf8') as json_file:
        json.dump(data['data'], json_file, ensure_ascii=False)

    ready_name = name + '_ready'

    abitur = db[name]
    ready_to_join = db[ready_name]

    db.drop_collection(name)

    with open(file_name, encoding="utf-8") as f:
        file_data = json.load(f)

    abitur.insert_many(file_data)
    abitur.update_many({}, {"$unset": {"index": 1}})
    db.drop_collection(ready_name)
    # db.drop_collection('telegram')

    cursor = abitur.find({'Согласие на зачисление': {'$regex': '✓'}})

    n = 1

    for document in cursor:
        if (document['Вид документа об образовании'] == "Копия") and (document["Доставка документов"] == "Веб"):
            continue
        document['Рейтинг'] = n
        n += 1
        ready_to_join.insert_one(document)


def update_links():
    # log = logging.getLogger(__name__)

    client = DbClient()

    db = client['abiturients']

    links_db = db['links']
    special_links_db = db['special_links']

    full_name_list = []
    special_name_list = []

    cursor = links_db.find({})

    for i in cursor:
        full_name_list.append(i['full_name'])
        special_name_list.append(i['special_name'])

    url = 'https://pstu.ru/enrollee/stat2022/poldoc2022/'

    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    tml = urllib.request.urlopen(req).read()

    soup = BeautifulSoup(tml, 'lxml')
    x = soup.findAll('a')[37:]

    for link in x:
        if link.text in full_name_list:
            print(link.text)
            filter = {"full_name": str(link.text)}
            new_link = {"$set": {'link': str('https://pstu.ru') + quote((link.attrs['href']))}}
            links_db.update_one(filter, new_link)

        elif link.text in special_name_list:
            print(link.text)
            filter = {"special_name": str(link.text)}
            new_link = {"$set": {'special_link': str('https://pstu.ru') + quote((link.attrs['href']))}}
            # print(new_link)
            links_db.update_one(filter, new_link)

    cursor = links_db.find({})
    # print(cursor)

    directions = ["pm", "ist", "fop", "ivk", "mm", "mie"]

    for i in cursor:
        print(i['_id'])
        url = str(i['link'])
        # log.info(i['_id'], url)
        get_json(url, i['_id'], db)

    return '*обновление файлов успешно завершено*'


if __name__ == "__main__":
    update_links()