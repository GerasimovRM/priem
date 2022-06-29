from typing import List

from pydantic import BaseModel


class StudentNotification(BaseModel):
    fio: str
    student_url: str
    directions: List[str]
    status: str
    time_send: str
    time_created: str
    last_moderator: str
    is_moderated: bool


class StudentNotificationData(BaseModel):
    students: List[StudentNotification]
