import ast
import configparser
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

config = configparser.RawConfigParser()
config.read_file(open('config.txt'))
webdriver_dir = config.get("config", "webdriver_dir")
username = config.get("config", "username")
password = config.get("config", "password")


def main():
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(webdriver_dir, options=options)
    driver.get(
        'http://authserver.cqu.edu.cn/authserver/login?service=http://my.cqu.edu.cn/authserver/authentication/cas')
    driver.find_element_by_id('username').clear()
    driver.find_element_by_id('username').send_keys(username)
    driver.find_element_by_id('password').clear()
    driver.find_element_by_id('password').send_keys(password)
    driver.find_element_by_class_name('auth_login_btn').click()
    driver.get('http://my.cqu.edu.cn/enroll/Home')
    time.sleep(5)
    agent = driver.execute_script('return localStorage.getItem("u__Access-Token");')
    driver.quit()
    token = ast.literal_eval(agent)["value"]
    print(token)


if __name__ == '__main__':
    main()
