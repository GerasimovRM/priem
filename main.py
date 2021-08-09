from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from settings import LOGIN, PASSWORD, BASE_URL
import time


driver = webdriver.Firefox()
# Login page
driver.get(f"{BASE_URL}/user/sign-in/login")
login_input = driver.find_element_by_id("loginform-identity")
login_input.send_keys(LOGIN)
password_input = driver.find_element_by_id("loginform-password")
password_input.send_keys(PASSWORD)
password_input.send_keys(Keys.RETURN)

#continue_button = driver.find_element_by_name("login-button")
# print(continue_button.tag_name)
#driver.implicitly_wait(10)
# Find people page
driver.refresh()
driver.get(f"{BASE_URL}/sandbox/all")
driver.implicitly_wait(10)
filters_open_button = driver.find_element_by_xpath(u"//a[")
filters_open_button.click()
print(filters_open_button)
fio_input = driver.find_element_by_id("applicationsearch-fio")
fio_input.send_keys("Герасимов Роман Михайлович")
#time.sleep(100)
driver.close()



