from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys

from settings import LOGIN, PASSWORD, BASE_URL, ZIP_DIR
import time


profile = webdriver.FirefoxProfile()
profile.set_preference("browser.download.folderList", 2)
profile.set_preference("browser.download.manager.showWhenStarting", False)
profile.set_preference("browser.download.dir", ZIP_DIR)
profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/zip")

driver = webdriver.Firefox(firefox_profile=profile)
# wait = WebDriverWait(driver, 10)

# Login page
driver.get(f"{BASE_URL}/user/sign-in/login")
login_input = driver.find_element_by_id("loginform-identity")
login_input.send_keys(LOGIN)
password_input = driver.find_element_by_id("loginform-password")
password_input.send_keys(PASSWORD)
password_input.send_keys(Keys.RETURN)
time.sleep(5)  # wait page load

# Find people page
driver.refresh()
with open("students.txt", encoding="utf-8") as students_file:
    students_fio = list(map(str.strip, students_file.readlines()))

for student_fio in students_fio:
    student_fio_short = (student_fio.split()[0] + " " +
                         "".join(list(map(lambda s: s[0] + ".", student_fio.split()[1:])))).lower()

    driver.get(f"{BASE_URL}/sandbox/all")

    filters_open_button = driver.find_element_by_xpath(u"//a[@data-toggle='collapse']")
    filters_open_button.click()

    fio_input = driver.find_element_by_id("applicationsearch-fio")
    fio_input.clear()
    fio_input.send_keys(student_fio)

    filter_button = driver.find_element_by_xpath(u"//button[@class='btn btn-primary']")
    filter_button.click()
    time.sleep(1)

    table = driver.find_element_by_tag_name("table")
    table_body = table.find_element_by_tag_name("tbody")
    table_trs = table_body.find_elements_by_tag_name("tr")
    student_count = 0
    for table_tr in table_trs:
        table_tds = table_tr.find_elements_by_tag_name("td")
        t = table_tds[3].text.lower()
        if table_tds[3].text.lower() != student_fio_short:
            continue
        student_count += 1
        table_tds[2].find_element_by_tag_name("a").click()
        time.sleep(2)

        driver.find_element_by_xpath("//a[@class='btn btn-info']").click()
    if student_count == 0:
        print(f"{student_fio} not found!")
    elif student_count > 1:
        print(f"{student_fio} ok!")
    else:
        print(f"{student_fio} duplicated!")





