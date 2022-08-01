from copy import copy
from typing import Optional, Union, List, Tuple
from configparser import ConfigParser
import os
import time

import selenium
from selenium.webdriver import FirefoxProfile, Firefox
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys


BASE_URL = "https://priem.pstu.ru"


class CustomFirefox:
    def __init__(self, basic_time_wait, is_hidden=True, *args, **kwargs):
        options = Options()
        if is_hidden:
            options.add_argument('--headless')
        self.basic_time_wait = basic_time_wait
        self.webdriver = Firefox(*args, options=options, **kwargs)
        self.wait_driver = WebDriverWait(self.webdriver, basic_time_wait)
        config = ConfigParser()
        config.read("config.ini")
        self.config = config
        self.login = config.get("MAIN", "LOGIN")
        self.password = config.get("MAIN", "PASSWORD")
        self.is_auth = False

    def auth(self):
        self.webdriver.get(f"{BASE_URL}/user/sign-in/login")
        login_input = self.webdriver.find_element(value="loginform-identity")
        login_input.send_keys(self.login)
        password_input = self.webdriver.find_element(value="loginform-password")
        password_input.send_keys(self.password)
        password_input.send_keys(Keys.RETURN)
        try:
            self.wait_driver.until(lambda driver: driver.find_element(value="applicationsearch-fio"))
        except TimeoutException:
            raise ValueError("Неверный логин или пароль")
        self.is_auth = True

    def close(self):
        self.webdriver.close()


class CustomFirefoxWithPath(CustomFirefox):
    def __init__(self,  direction_zip_path, basic_time_wait, *args, **kwargs):
        downloader_base_profile = FirefoxProfile()
        downloader_base_profile.set_preference("browser.download.folderList", 2)
        downloader_base_profile.set_preference("browser.download.manager.showWhenStarting", False)
        downloader_base_profile.set_preference("browser.download.dir", direction_zip_path)
        downloader_base_profile.set_preference("browser.helperApps.neverAsk.saveToDisk",
                                               "application/zip")

        super().__init__(basic_time_wait, *args, firefox_profile=downloader_base_profile, **kwargs)


class FromCiteToArchive:
    header_structure = ["id_on_page",
                        "is_locked",
                        "check_button",
                        "fio", "email",
                        "company",
                        "country",
                        "is_id_exist",
                        "target_priem",
                        "special_priem",
                        "directions",
                        ...]

    def __init__(self,
                 config_path,
                 basic_wait_time: Optional[int] = None):

        config = ConfigParser()
        config.read(config_path)
        self.config = config

        zip_dir = f'{os.getcwd()}\\{config.get("MAIN", "ZIP_DIR")}'
        if not os.path.isdir(zip_dir):
            os.mkdir(zip_dir)
        self.zip_dir = zip_dir

        if not basic_wait_time:
            basic_wait_time = 10

        self.searcher = CustomFirefox(basic_wait_time)
        self.searcher.auth()

        self.current_direction = None
        self.direction_downloaders = {}
    
    def create_downloader_for_direction(self, direction_name: str = "") -> CustomFirefoxWithPath:
        zip_dir = f'{os.getcwd()}\\{self.config.get("MAIN", "ZIP_DIR")}\\{direction_name}'
        if not os.path.isdir(zip_dir):
            os.mkdir(zip_dir)

        if self.current_direction is None:
            self.current_direction = direction_name
        elif self.current_direction != direction_name:
            self.direction_downloaders[self.current_direction].close()
            self.direction_downloaders.pop(self.current_direction)
            self.current_direction = direction_name

        if direction_name in self.direction_downloaders:
            downloader = self.direction_downloaders[direction_name]
        else:
            downloader = CustomFirefoxWithPath(zip_dir, self.searcher.basic_time_wait)
            self.direction_downloaders[direction_name] = downloader
            downloader.auth()
        return downloader

    def find_person_and_load_data(self, student_fio: Union[str, List[str]],
                                  direction_name: Optional[str] = None):
        if direction_name:
            downloader = self.create_downloader_for_direction(direction_name)
        else:
            downloader = self.create_downloader_for_direction()

        if isinstance(student_fio, list):
            student_fio = " ".join(student_fio)

        self.searcher.webdriver.execute_script("location.reload(true);")

        self.searcher.webdriver.get(f"https://priem.pstu.ru/sandbox/all?ApplicationSearch[statusBlock]=&ApplicationSearch[fio]={student_fio}&ApplicationSearch[usermail]=&ApplicationSearch[guid]=&ApplicationSearch[campaign_code]=&ApplicationSearch[citizenship]=&ApplicationSearch[hasIndividualAchievement]=&ApplicationSearch[targetReception]=&ApplicationSearch[preferences]=&ApplicationSearch[specialityName]=&ApplicationSearch[educationForm]=&ApplicationSearch[status]=&ApplicationSearch[sent_at]=&ApplicationSearch[to_sent_at]=&ApplicationSearch[created_at]=&ApplicationSearch[to_created_at]=&ApplicationSearch[last_management_at]=&ApplicationSearch[to_last_management_at]=&ApplicationSearch[lastManagerName]=&ApplicationSearch[historyChanges]=")
        is_empty = False
        try:
            WebDriverWait(self.searcher.webdriver, 3).until(lambda driver: driver.find_element(By.CLASS_NAME, "empty"))
            is_empty = True
        except TimeoutException:
            table_body = self.searcher.webdriver.find_element(By.TAG_NAME, "tbody")
            table_trs = table_body.find_elements(By.TAG_NAME, "tr")
            student_ids = list(map(lambda t: t.get_attribute("data-key"), table_trs))
            for student_id in student_ids:
                downloader.webdriver.get(f"{BASE_URL}/sandbox/view?id={student_id}")
                try:
                    downloader.webdriver.find_element(By.XPATH, "//a[@class='btn btn-info']").click()
                except NoSuchElementException:
                    is_empty = True
        if is_empty:
            print(f"{student_fio} не найден!")
        else:
            print(f"{student_fio} ok!")
    
    def close_all_webdrivers(self):
        self.searcher.close()
        self.direction_downloaders[self.current_direction].close()
