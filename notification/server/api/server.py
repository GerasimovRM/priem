import datetime
from typing import Optional

from fastapi import FastAPI
import asyncio

from starlette.websockets import WebSocket, WebSocketDisconnect
from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK

from notification.server.config import WEBSOCKET_TIME_WAIT, SERVER_PARSER_WAIT
from notification.server.core.parser import ParserNotificator
from notification.server.models.student_data import StudentNotificationData
from notification.server.core.common import debug_print

from fastapi_utils.tasks import repeat_every

app = FastAPI(docs_url="/")
parser: Optional[ParserNotificator] = None
is_loaded = False


@app.on_event("startup")
@repeat_every(seconds=SERVER_PARSER_WAIT)
def on_startup():
    global parser
    global is_loaded
    if not parser:
        parser = ParserNotificator()
    debug_print(datetime.datetime.now(), "Парсинг...")
    parser.parse_new_students()
    is_loaded = True
    debug_print(datetime.datetime.now(), "Парсинг завершен!")
    debug_print("Students Data:", parser.notifications)


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
    debug_print(parser.notifications)
    for i, item in enumerate(students):
        if item.fio == fio and item.student_url == student_url:
            students[i].is_moderated = is_moderated
            students[i].computer_name = computer_name if is_moderated else None
    debug_print(parser.notifications)


@app.websocket("/")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            if parser and is_loaded:
                await websocket.send_json(parser.notifications.dict())
                data = await websocket.receive_text()
            await asyncio.sleep(WEBSOCKET_TIME_WAIT)
    except (WebSocketDisconnect, ConnectionClosedError, ConnectionClosedOK):
        pass
