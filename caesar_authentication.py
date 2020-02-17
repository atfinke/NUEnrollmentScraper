import logging

from time import sleep
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.alert import Alert

from utils import wait, load_main_page


def is_authenticated(driver, timeout=10):
    try:
        load_main_page(driver, timeout)
    except:
        print("is_authenticated: False")
        return False

    print("is_authenticated: True")
    return True


def authenticate(driver, username, password):
    print("authenticate: Starting Caesar Log In")

    max_attempts = 2
    for i in range(max_attempts):
        url = "https://caesar.ent.northwestern.edu/"
        driver.get(url)

        delay = 10
        try:
            wait(driver, 'IDToken1', delay)
            break
        except:
            print("authenticate: Loading took too much time!")
            driver.delete_all_cookies()
            if i == max_attempts - 1:
                return False

    inputElement = driver.find_element_by_id("IDToken1")
    inputElement.send_keys(username)
    inputElement = driver.find_element_by_id("IDToken2")
    inputElement.send_keys(password)

    driver.execute_script("LoginSubmit('Log In')")

    # Sleeping until 2FA page loaded
    sleep(5)

    try:
        remember_radio = driver.find_elements_by_class_name('row')[1].find_element_by_id('IDToken0')
        remember_radio.click()
    except:
        try:
            return is_authenticated(driver)
        except:
            print("authenticate: No remember button...")
            return False

    driver.execute_script("LoginSubmit('Continue')")
    print("authenticate: Waiting for 2FA approval...")
    return is_authenticated(driver, 30)
