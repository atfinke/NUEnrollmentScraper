from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC


def load_main_page(driver, timeout):
    driver.get('https://caesar.ent.northwestern.edu/')
    wait(driver, 'PTNUI_LAND_WRK_GROUPBOX14$PIMG', timeout)


def wait(driver, element_id, delay):
    try:
        element = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, element_id)))
        return element
    except TimeoutException:
        raise ValueError("wait: Loading took too much time!")


def click(driver, element):
    driver.execute_script("arguments[0].click();", element)
