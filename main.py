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
student_fio = "Волохова Дарья Юрьевна"
student_fio_short = (student_fio.split()[0] + " " +
                     "".join(list(map(lambda s: s[0] + ".", student_fio.split()[1:])))).lower()

driver.get(f"{BASE_URL}/sandbox/all")

filters_open_button = driver.find_element_by_xpath(u"//a[@data-toggle='collapse']")
filters_open_button.click()

fio_input = driver.find_element_by_id("applicationsearch-fio")
fio_input.send_keys(student_fio)

filter_button = driver.find_element_by_xpath(u"//button[@class='btn btn-primary']")
filter_button.click()
time.sleep(1)

table = driver.find_element_by_tag_name("table")
table_body = table.find_element_by_tag_name("tbody")
table_trs = table_body.find_elements_by_tag_name("tr")
for table_tr in table_trs:
    table_tds = table_tr.find_elements_by_tag_name("td")
    t = table_tds[3].text.lower()
    if table_tds[3].text.lower() != student_fio_short:
        continue

    table_tds[2].find_element_by_tag_name("a").click()
    time.sleep(2)

    driver.find_element_by_xpath("//a[@class='btn btn-info']").click()



