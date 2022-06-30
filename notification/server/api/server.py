import json
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel
import websockets
import asyncio

from starlette.websockets import WebSocket, WebSocketDisconnect

from notification.server.core.parser import ParserNotificator
from notification.server.models.student_data import StudentNotificationData

from fastapi_utils.tasks import repeat_every

app = FastAPI(docs_url="/")
parser = ParserNotificator()


@repeat_every(seconds=60 * 5)
async def get_data_from_site():
    parser.parse_new_students()


@app.get("/get_data", response_model=StudentNotificationData)
async def get_data():
    return parser.notifications


@app.put("/student")
async def put_student(fio: str,
                      student_url: str,
                      computer_name: str):
    students = parser.notifications.students
    # TODO: убрать подходы из деревни
    print(parser.notifications)
    for i, item in enumerate(students):
        if item.fio == fio and item.student_url == student_url:
            students[i].is_moderated = True
            students[i].computer_name = computer_name
    print(parser.notifications)


@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(parser.notifications.dict())
            data = await websocket.receive_text()
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        pass
