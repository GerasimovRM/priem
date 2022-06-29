from typing import Optional

from selenium.webdriver import FirefoxProfile, Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

from ..config import BASE_TIME_WAIT, LOGIN, PASSWORD, PARSER_URL

class Parser:
    def __init__(self, basic_time_wait: Optional[int] = None):
        with open("directions.txt", encoding="utf-8") as input_file:
            self.directions = input_file.read().split("\n")
        self.searcher = Firefox()
        if basic_time_wait:
            self.basic_time_wait = basic_time_wait
        else:
            self.basic_time_wait = BASE_TIME_WAIT

        self.login = LOGIN
        self.password = PASSWORD
        self.is_auth = False

    def auth(self) -> bool:
        if self.is_auth:
            return True
        self.searcher.get(f"{PARSER_URL}/user/sign-in/login")
        login_input = self.searcher.find_element(value="loginform-identity")
        login_input.send_keys(self.login)
        password_input = self.searcher.find_element(value="loginform-password")
        password_input.send_keys(self.password)
        password_input.send_keys(Keys.RETURN)

        # auth validation
        try:
            self.wait_searcher.until(lambda driver: driver.find_element(value="applicationsearch-fio"))
        except TimeoutException:
            raise ValueError("Неверный логин или пароль")
        self.is_auth = True


    def parse_new_students(self):
        pass

