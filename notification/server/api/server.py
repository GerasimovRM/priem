import json
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel
import websockets
import asyncio

from starlette.websockets import WebSocket, WebSocketDisconnect

from notification.server.core.parser import ParserNotificator
from notification.server.models.student_data import StudentNotificationData

app = FastAPI(docs_url="/")
parser = ParserNotificator()


class TestData(BaseModel):
    fio: str
    test: str


@app.get("/get_data", response_model=StudentNotificationData)
async def get_data():
    return parser.notifications


@app.put("/student")
async def put_student(fio: str,
                      student_url: str):
    students = parser.notifications.students
    # TODO: убрать подходы из деревни
    print(parser.notifications)
    for i, item in enumerate(students):
        if item.fio == fio and item.student_url == student_url:
            students[i].is_moderated = True
    print(parser.notifications)


@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    # test_data = TestData(fio="123", test="testr")
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(parser.notifications.dict())
            data = await websocket.receive_text()
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        pass
