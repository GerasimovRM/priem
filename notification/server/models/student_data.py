from typing import List, Optional

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
    computer_name: Optional[str] = None


class StudentNotificationData(BaseModel):
    students: List[StudentNotification]
