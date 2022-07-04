from typing import Optional

from selenium.webdriver import FirefoxProfile, Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

from notification.server.config import BASE_TIME_WAIT,\
    LOGIN, PASSWORD, PARSER_URL, SERVER_ADDRESS, DEBUG
from notification.server.core.common import debug_print
from notification.server.models.student_data import StudentNotificationData, StudentNotification
from selenium.webdriver.support import expected_conditions as EC


class ParserNotificator:
    def __init__(self, basic_time_wait: Optional[int] = None):
        with open("directions.txt", encoding="utf-8") as input_file:
            self.directions = set(input_file.read().split("\n"))
        if basic_time_wait:
            self.basic_time_wait = basic_time_wait
        else:
            self.basic_time_wait = BASE_TIME_WAIT
        options = Options()
        options.add_argument('--headless')
        self.searcher = Firefox(options=options)
        self.wait_searcher = WebDriverWait(self.searcher, self.basic_time_wait)
        self.login = LOGIN
        self.password = PASSWORD
        self.is_auth = False
        self.notifications: StudentNotificationData = StudentNotificationData(students=[])
        self.main_page_url = None
        # self.parse_new_students()

    def auth(self) -> bool:
        # TODO: log time answer => except value error
        if self.is_auth:
            return True
        self.searcher.get(f"{PARSER_URL}/user/sign-in/login")
        login_input = self.searcher.find_element(value="loginform-identity")
        login_input.send_keys(self.login)
        password_input = self.searcher.find_element(value="loginform-password")
        password_input.send_keys(self.password)
        password_input.send_keys(Keys.RETURN)
        try:
            # self.wait_searcher.until(lambda driver: driver.find_element(By.ID, value="applicationsearch-fio"))
            self.wait_searcher.until(EC.presence_of_element_located((By.ID, "applicationsearch-fio")))

        except TimeoutException:
            raise ValueError("Неверный логин или пароль")
        self.is_auth = True
        self.main_page_url = self.searcher.current_url

    def parse_new_students(self):
        if not self.is_auth:
            self.auth()
        new_notifications = []
        page_count = 1
        while True:
            self.searcher.get(f"{self.main_page_url}?page={page_count}")
            try:
                WebDriverWait(self.searcher, 1).until(lambda driver: driver.find_element(By.CLASS_NAME, "empty"))
            except TimeoutException:
                table_body = self.searcher.find_element(By.TAG_NAME, "tbody")
                table_trs = table_body.find_elements(By.TAG_NAME, "tr")
                first_td = table_trs[0].find_element(By.TAG_NAME, "td")
                first_id_on_page = int(first_td.text)
                if (page_count - 1) * 20 + 1 != first_id_on_page:
                    break
                for tr in table_trs:
                    tds = tr.find_elements(By.TAG_NAME, "td")
                    directions = set(map(str.strip, tds[10].text.split(","))) & self.directions
                    if not directions:
                        continue

                    student_link_td = tds[2]
                    student_link = student_link_td.find_element(By.CLASS_NAME, "btn").get_attribute(
                        "href")
                    fio = tds[3].text
                    status = tds[12].text
                    time_send = tds[13].text
                    time_created = tds[14].text
                    last_moderator = tds[16].text
                    if DEBUG:
                        debug_print("=====", fio, student_link, directions, status, time_send, time_created, last_moderator, "=====", sep='\n')
                    old_student_data = next(filter(lambda x: x.fio == fio and x.student_url == student_link, self.notifications.students), None)
                    is_moderated = False
                    if old_student_data:
                        is_moderated = old_student_data.is_moderated
                    new_notifications.append(StudentNotification(fio=fio,
                                                                 student_url=student_link,
                                                                 directions=directions,
                                                                 status=status,
                                                                 time_send=time_send,
                                                                 time_created=time_created,
                                                                 last_moderator=last_moderator,
                                                                 is_moderated=is_moderated))

            page_count += 1
        debug_print("PageCount:", page_count)
        self.notifications = StudentNotificationData(students=new_notifications)

