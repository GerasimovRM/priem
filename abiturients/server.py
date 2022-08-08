import json
from enum import Enum
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException

from mongo_client import DbClient
from common import group_names

app = FastAPI(docs_url="/")

exclude_data = {"ist": 63, "fop": 22, "pm": 38, "ivk": 23, "mie": 22, "mm": 37}
delete_keys = ["Подтверждающий документ (целевого направления)", "Преимущ.право"]
students_codes = {}


def update_rating(abiturients, enumerate_with=1):
    abiturients = [{k: v if v else "-" for k, v in abiturient.items() if k not in delete_keys} for
                   abiturient in abiturients]
    return list(map(lambda abit_data: {"Рейтинг в текущем списке": abit_data[0]} | abit_data[1],
                    enumerate(abiturients, enumerate_with)))


def add_students_names(abiturients):
    return list(map(lambda abit_data: dict(zip(["ФИО", "_____Номер_____", "Почта"],
                                               students_codes[abit_data["_id"]] if abit_data[
                                                                                       "_id"] in students_codes else [
                                                   "-", "-", "-"])) | abit_data, abiturients))


@app.on_event("startup")
def get_students_codes():
    global students_codes
    with open("students.json", encoding="utf8") as json_file:
        students_codes = json.load(json_file)


@app.get("/links")
async def links():
    client = DbClient()
    abiturients = client["abiturients"]
    return list(abiturients["links"].find({}))


@app.get("/names")
async def links():
    client = DbClient()
    abiturients = client["abiturients"]
    return update_rating(add_students_names(abiturients["names"].find({})))


@app.get("/get_default")
async def get_default():
    client = DbClient()
    abiturients = client["abiturients"]
    return {group_name: update_rating(add_students_names(abiturients[group_name].find({}))) for
            group_name in group_names}


@app.get("/get_original_docs_without_agreement")
async def get_original_docs_without_agreement():
    client = DbClient()
    query = {"Вид документа об образовании": "Оригинал", "Согласие на зачисление": None}
    abiturients = client["abiturients"]
    return {group_name: update_rating(add_students_names(abiturients[group_name].find(query))) for
            group_name in group_names}


@app.get("/get_agreement_without_original_docs")
async def get_agreement_without_original_docs():
    client = DbClient()
    query = {"Вид документа об образовании": "Копия", "Согласие на зачисление": "✓"}
    abiturients = client["abiturients"]
    return {group_name: update_rating(add_students_names(abiturients[group_name].find(query))) for
            group_name in group_names}


@app.get("/get_agreement_with_original_docs")
async def get_agreement_with_original_docs():
    client = DbClient()
    abiturients = client["abiturients"]
    query = {"$or": [
        {
            "Вид документа об образовании": "Оригинал",
            "Согласие на зачисление": "✓",
            "Доставка документов": "Веб"
        },
        {
            "Согласие на зачисление": "✓",
            "Доставка документов": "Суперсервис"
        }]}
    return {group_name: update_rating(add_students_names(abiturients[group_name].find(query))) for
            group_name in group_names}


@app.get("/get_exclude_peoples")
async def get_exclude_peoples():
    client = DbClient()
    abiturients = client["abiturients"]
    query = {"Вид документа об образовании": "Оригинал", "Согласие на зачисление": "✓"}
    return {group_name: update_rating(
        add_students_names(abiturients[group_name].find(query)[exclude_data[group_name]:]),
        enumerate_with=exclude_data[group_name] + 1) for group_name in group_names}


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=5000, log_level="info", reload=True)
