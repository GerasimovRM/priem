from typing import Optional, Union, List
from configparser import ConfigParser
import os
import time

from selenium.webdriver import FirefoxProfile, Firefox
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys


BASE_URL = "https://priem.pstu.ru"


class FromCiteToArchive:
    def __init__(self,
                 config_path,
                 searcher_profile: Optional[FirefoxProfile] = None,
                 basic_wait_time: Optional[int] = None):

        config = ConfigParser()
        config.read(config_path)
        login = config.get("main", "LOGIN")
        password = config.get("main", "PASSWORD")

        zip_dir = config.get("main", "ZIP_DIR")
        if not os.path.isdir(zip_dir):
            os.mkdir(zip_dir)

        if not searcher_profile:
            searcher_profile = FirefoxProfile()
            searcher_profile.set_preference("browser.download.folderList", 2)
            searcher_profile.set_preference("browser.download.manager.showWhenStarting", False)
            searcher_profile.set_preference("browser.download.dir", zip_dir)
            searcher_profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/zip")

        if not basic_wait_time:
            basic_wait_time = 10

        self.searcher = Firefox()
        self.downloader = Firefox(firefox_profile=searcher_profile)
        self.wait_searcher = WebDriverWait(self.searcher, basic_wait_time)
        self.wait_downloader = WebDriverWait(self.searcher, basic_wait_time)

        self.login = login
        self.password = password
        self.is_auth = False

    def auth(self) -> bool:
        if self.is_auth:
            return True
        self.searcher.get(f"{BASE_URL}/user/sign-in/login")
        login_input = self.searcher.find_element_by_id("loginform-identity")
        login_input.send_keys(self.login)
        password_input = self.searcher.find_element_by_id("loginform-password")
        password_input.send_keys(self.password)
        password_input.send_keys(Keys.RETURN)

        self.downloader.get(f"{BASE_URL}/user/sign-in/login")
        login_input = self.downloader.find_element_by_id("loginform-identity")
        login_input.send_keys(self.login)
        password_input = self.downloader.find_element_by_id("loginform-password")
        password_input.send_keys(self.password)
        password_input.send_keys(Keys.RETURN)
        # auth validation
        try:
            self.wait_searcher.until(lambda driver: driver.find_element_by_id("applicationsearch-fio"))
            self.wait_downloader.until(lambda driver: driver.find_element_by_id("applicationsearch-fio"))
        except TimeoutException:
            raise ValueError("Неверный логин или пароль")
        self.is_auth = True

    def find_person_and_load_data(self, student_fio: Union[str, List[str]]):
        if isinstance(student_fio, list):
            student_fio = " ".join(student_fio)
        if not self.is_auth:
            self.auth()

        self.searcher.execute_script("location.reload(true);")

        self.searcher.get(f"https://priem.pstu.ru/sandbox/all?ApplicationSearch[statusBlock]=&ApplicationSearch[fio]={student_fio}&ApplicationSearch[usermail]=&ApplicationSearch[guid]=&ApplicationSearch[campaign_code]=&ApplicationSearch[citizenship]=&ApplicationSearch[hasIndividualAchievement]=&ApplicationSearch[targetReception]=&ApplicationSearch[preferences]=&ApplicationSearch[specialityName]=&ApplicationSearch[educationForm]=&ApplicationSearch[status]=&ApplicationSearch[sent_at]=&ApplicationSearch[to_sent_at]=&ApplicationSearch[created_at]=&ApplicationSearch[to_created_at]=&ApplicationSearch[last_management_at]=&ApplicationSearch[to_last_management_at]=&ApplicationSearch[lastManagerName]=&ApplicationSearch[historyChanges]=")
        is_empty = False
        try:
            WebDriverWait(self.searcher, 1).until(lambda driver: driver.find_element_by_class_name("empty"))
            is_empty = True
        except TimeoutException:
            table_body = self.searcher.find_element_by_tag_name("tbody")
            table_trs = table_body.find_elements_by_tag_name("tr")
            student_ids = list(map(lambda t: t.get_attribute("data-key"), table_trs))
            for student_id in student_ids:
                self.downloader.get(f"{BASE_URL}/sandbox/view?id={student_id}")
                self.downloader.find_element_by_xpath("//a[@class='btn btn-info']").click()
        if is_empty:
            print(f"{student_fio} не найден!")
        else:
            print(f"{student_fio} ok!")
    
    def close(self):
        self.searcher.close()
        time.sleep(10)
        self.downloader.close()