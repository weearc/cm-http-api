import ast
import configparser
import json
import os
import time
from datetime import datetime

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.support.wait import WebDriverWait

__all__ = ('cm_http',)


def load_config(configfile):
    config = configparser.RawConfigParser()
    try:
        if os.path.exists(configfile):
            config.read_file(open(configfile))
            webdriver_dir = config.get("config", "webdriver_dir")
            username = config.get("config", "username")
            password = config.get("config", "password")
            try:
                if all([username, password, webdriver_dir]) is False:
                    raise ConfigEmptyException
                else:
                    return webdriver_dir, username, password
            finally:
                pass
        else:
            raise NoneConfigFileExpection
    finally:
        pass


class cm_http():
    """

    Args:
        username (str): authserver username
        password (str): authserver password
        webdriver_dir (str, optional): path of webdriver. Defaults to "chromedriver".
    """

    def __init__(self, username, password, webdriver_dir="chromedriver"):
        self.username = username
        self.password = password
        self.webdriver_dir = webdriver_dir
        self.driver = None

    def start_webdriver(self, force=False):
        """Start webdriver

        Args:
            force (bool, optional): restart even if webdriver is running. Defaults to False.

        Returns:
            webdriver: webdriver started
        """
        if self.driver is not None:
            if force or not self.driver.service.process:
                self.driver.quit()
            else:
                return self.driver
        # https://stackoverflow.com/questions/52633697/selenium-python-how-to-capture-network-traffics-response
        capabilities = DesiredCapabilities.CHROME
        capabilities["goog:loggingPrefs"] = {"performance": "ALL"}
        options = Options()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(
            self.webdriver_dir,
            options=options,
            desired_capabilities=capabilities)
        return self.driver

    def stop_webdriver(self):
        """Stop webdriver. It should be manually called after all operation are done.
        """
        if self.driver is not None:
            self.driver.quit()

    def login(self, force=False):
        """Log in http://my.cqu.edu.cn/enroll/. No need to manually call `start_webdriver`.

        Args:
            force (bool, optional): relogin even if in logined status. Defaults to False.

        Returns:
            bool: whether login is successful
        """
        self.start_webdriver()
        self.driver.get('http://my.cqu.edu.cn/enroll/Home')
        if force or self.driver.current_url.startswith('http://authserver.cqu.edu.cn/authserver/login'):
            self.driver.find_element_by_id('username').clear()
            self.driver.find_element_by_id('username').send_keys(self.username)
            self.driver.find_element_by_id('password').clear()
            self.driver.find_element_by_id('password').send_keys(self.password)
            self.driver.find_element_by_class_name('auth_login_btn').click()
        return self.driver.current_url.startswith('http://my.cqu.edu.cn/enroll/Home')

    def get_timetable_by_request(self):
        """Get timetable using requests
        :exception Network Error
                    Server Error
        :return: json
        """
        enroll_api = 'http://my.cqu.edu.cn/enroll-api/timetable/student/' + self.get_student_num()
        ua = self.driver.execute_script("return navigator.userAgent;")
        headers = {
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Accept": "application/json, text/plain, */*",
        }
        auth = "Bearer " + self.get_token()['value']
        headers["User-Agent"] = ua
        headers["Authorization"] = auth

        re = requests.get(url=enroll_api, headers=headers)
        return re.json()

    def get_student_num(self):
        """Get student number from http://my.cqy.edu.cn/enroll/

        :return: str
        """
        self.login()
        wait = WebDriverWait(self.driver, 5)
        try:
            wait.until(presence_of_element_located(
                (By.CLASS_NAME, 'pcStudentScheduleBtn')))
        except Exception as e:
            time.sleep(10)

        self.driver.get_log("performance")  # clean log
        self.driver.find_element_by_xpath('//*[@id="app"]/section/header/div/div[2]/div/div').click()
        stu_num = self.driver.find_element_by_class_name('info-item.user-code').get_attribute('textContent')
        return stu_num

    def get_timetable(self):
        """Get timetable data. No need to manually call `start_webdriver` and/or `login`.

        Raises:
            Exception: Something unexpected.

        Returns:
            dict: timetable data
        """
        self.login()
        wait = WebDriverWait(self.driver, 5)
        try:
            wait.until(presence_of_element_located(
                (By.CLASS_NAME, 'pcStudentScheduleBtn')))
        except Exception as e:
            time.sleep(10)

        self.driver.get_log("performance")  # clean log
        self.driver.find_element_by_class_name('pcStudentScheduleBtn').click()
        wait.until(presence_of_element_located(
            (By.CLASS_NAME, 'week-day-box')))

        log = self.driver.get_log("performance")
        net_log = (json.loads(i['message'])['message']
                   for i in log)
        for i in net_log:
            if i['method'] == 'Network.responseReceived' and \
                    i['params']['response']['url'].startswith(
                        'http://my.cqu.edu.cn/enroll-api/timetable/student/'):
                return json.loads(self.driver.execute_cdp_cmd(
                    'Network.getResponseBody',
                    {'requestId': i["params"]["requestId"]})['body']
                                  )
        else:
            raise Exception()

    def get_token(self):
        """Get token and its expiration time

        Returns:
            dict: {'value': token in `str`, 'expire': expiration time in `datetime`}
        """
        self.login()
        wait = WebDriverWait(self.driver, 5)
        try:
            wait.until(presence_of_element_located(
                (By.CLASS_NAME, 'pcStudentScheduleBtn')))
        except Exception as e:
            time.sleep(5)
        agent = self.driver.execute_script(
            'return localStorage.getItem("u__Access-Token");')
        token = ast.literal_eval(agent)
        token['expire'] = datetime.fromtimestamp(token['expire'] / 10 ** 3)
        return token


class NoneConfigFileExpection(Exception):
    def __init__(self):
        pass

    def __str__(self):
        print("Cannot find config file.")


class ConfigEmptyException(Exception):
    def __init__(self):
        pass

    def __str__(self):
        print("Config error, please check it again.")


def main():
    webdriver_dir, username, password = load_config('config.txt')
    print(webdriver_dir, password, username)
    cm = cm_http(username=username, password=password,
                 webdriver_dir=webdriver_dir)
    cm.get_timetable_by_request()
    timetable_dict = cm.get_timetable()
    json.dump(timetable_dict, open('timetable.json', 'w'), ensure_ascii=False, indent=2)
    print('Timetable is saved to timetable.json')
    token = cm.get_token()
    print("Token:", token["value"])
    print("Token expiration time:", datetime.strftime(
        token['expire'], '%Y-%m-%d %H:%M:%S'))
    cm.stop_webdriver()


if __name__ == '__main__':
    main()
