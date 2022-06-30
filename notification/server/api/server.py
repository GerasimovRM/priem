import datetime
import json
from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel
import websockets
import asyncio

from starlette.websockets import WebSocket, WebSocketDisconnect
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

from notification.server.core.parser import ParserNotificator
from notification.server.models.student_data import StudentNotificationData

from fastapi_utils.tasks import repeat_every

app = FastAPI(docs_url="/")
parser: Optional[ParserNotificator] = None


@app.on_event("startup")
@repeat_every(seconds=60 * 5)
def on_startup():
    global parser
    if not parser:
        parser = ParserNotificator()
    print(datetime.datetime.now(), "Парсинг...")
    parser.parse_new_students()
    print(datetime.datetime.now(), "Парсинг завершен!")
    print("Students Data:", parser.notifications)


@app.get("/get_data", response_model=StudentNotificationData)
async def get_data():
    return parser.notifications


@app.put("/student")
async def put_student(fio: str,
                      student_url: str,
                      computer_name: str,
                      is_moderated: bool):
    students = parser.notifications.students
    # TODO: убрать подходы из деревни
    print(parser.notifications)
    for i, item in enumerate(students):
        if item.fio == fio and item.student_url == student_url:
            students[i].is_moderated = is_moderated
            students[i].computer_name = computer_name if is_moderated else None
    print(parser.notifications)


@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            if parser:
                await websocket.send_json(parser.notifications.dict())
                data = await websocket.receive_text()
            await asyncio.sleep(10)
    except (WebSocketDisconnect, ConnectionClosedError, ConnectionClosedOK):
        pass
