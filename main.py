import ast
import configparser
import time
import json

from selenium import webdriver
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By

from selenium.webdriver.chrome.options import Options

config = configparser.RawConfigParser()
config.read_file(open('config.txt'))
webdriver_dir = config.get("config", "webdriver_dir")
username = config.get("config", "username")
password = config.get("config", "password")


def main():
    # https://stackoverflow.com/questions/52633697/selenium-python-how-to-capture-network-traffics-response
    capabilities = DesiredCapabilities.CHROME
    capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
    options = Options()
    # options.add_argument('--headless')
    driver = webdriver.Chrome(
        webdriver_dir, options=options, desired_capabilities=capabilities)
    wait = WebDriverWait(driver, 5)

    driver.get('http://my.cqu.edu.cn/enroll/Home')
    # driver.get(
    #    'http://authserver.cqu.edu.cn/authserver/login?service=http://my.cqu.edu.cn/authserver/authentication/cas')
    if driver.current_url.startswith('http://authserver.cqu.edu.cn/'):
        driver.find_element_by_id('username').clear()
        driver.find_element_by_id('username').send_keys(username)
        driver.find_element_by_id('password').clear()
        driver.find_element_by_id('password').send_keys(password)
        driver.find_element_by_class_name('auth_login_btn').click()
    wait.until(presence_of_element_located(
        (By.CLASS_NAME, 'pcStudentScheduleBtn')))

    driver.get_log("performance")
    driver.find_element_by_class_name('pcStudentScheduleBtn').click()
    wait.until(presence_of_element_located((By.CLASS_NAME, 'week-day-box')))

    log = driver.get_log("performance")
    net_log = (json.loads(i['message'])['message']
               for i in log)
    for i in net_log:
        if i['method'] == 'Network.responseReceived' and \
                i['params']['response']['url'].startswith(
                'http://my.cqu.edu.cn/enroll-api/timetable/student/'):
            timetable_json = driver.execute_cdp_cmd('Network.getResponseBody', {
                'requestId': i["params"]["requestId"]})['body']
            break
    else:
        raise Exception()

    agent = driver.execute_script(
        'return localStorage.getItem("u__Access-Token");')
    driver.quit()
    token = ast.literal_eval(agent)["value"]
    # print(token)
    print(timetable_json)


if __name__ == '__main__':
    main()
