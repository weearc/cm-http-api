from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait                            # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC
import time


def main():
    student_num = ''
    # driver = webdriver.PhantomJS('../webdriver-phantomjs/phantomjs')

    driver = webdriver.Chrome("../webdriver-chrome/chromedriver")
    options = Options()
    options.add_argument('--headless')
    driver.get('http://authserver.cqu.edu.cn/authserver/login?service=http://my.cqu.edu.cn/authserver/authentication/cas')
    driver.find_element_by_id('username').clear()
    driver.find_element_by_id('username').send_keys('')
    driver.find_element_by_id('password').clear()
    driver.find_element_by_id('password').send_keys('')
    driver.find_element_by_class_name('auth_login_btn').click()
    driver.get('http://my.cqu.edu.cn/enroll/Home')
    time.sleep(5)
    # WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.XPATH, '//*[@id="app"]/section/section/main/div/div/div/div/div/div[2]/div[1]/div[1]/button')))
    # driver.find_element_by_xpath('//*[@id="app"]/section/section/main/div/div/div/div/div/div[2]/div[1]/div[1]/button').click()
    # WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.XPATH, "/html/body/div[3]/div/div[2]/div/div/div[2]/div/div[1]/div[2]/div/button")))
    # driver.find_element_by_xpath('/html/body/div[3]/div/div[2]/div/div/div[2]/div/div[1]/div[2]/div/button').click()
    print(driver.page_source)
    driver.quit()

if __name__ == '__main__':
    main()
