import pickle
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By

import secrets
from utils import load_main_page, wait, click
from caesar_authentication import authenticate, is_authenticated

CLASS_NUMBERS_TO_CHECK = [32701, 33510, 37987, 34338, 32448, 32455, 32468, 38006, 34321, 33715, 31916, 35867, 31712]


def load_cookies(driver):
    driver.get('https://www.northwestern.edu/')
    wait(driver, 'department', 5)
    cookies = pickle.load(open("cookies.pkl", "rb"))
    for cookie in cookies:
        if '.northwestern.edu' == cookie['domain']:
            driver.add_cookie(cookie)


def authenticate_if_needed(driver):
    if not is_authenticated(driver):
        authenticate(driver, secrets.netid, secrets.password)


def open_manage_classes(driver):
    load_main_page(driver, 10)
    button = wait(driver, 'win0divPTNUI_LAND_REC_GROUPLET$6', 15)
    click(driver, button)
    sleep(1)


def parse_shopping_cart(driver):
    driver.get('https://caesar.ent.northwestern.edu/psc/CS857PRD/EMPLOYEE/SA/c/SA_LEARNER_SERVICES_2.SSR_SSENRL_CART.GBL?pslnkid=NW_SS_SA_SHOPPING_CART&Page=SSR_SSENRL_CART&ICAGTarget=start')
    button = wait(driver, 'SSR_DUMMY_RECV1$sels$1$$0', 5)
    click(driver, button)
    button = wait(driver, 'DERIVED_SSS_SCT_SSR_PB_GO', 10)
    click(driver, button)

    sleep(1)
    iframe = wait(driver, 'ptifrmtgtframe', 10)
    driver.get(iframe.get_attribute("src"))
    sleep(1)

    table = wait(driver, 'SSR_REGFORM_VW$scroll$0', 10)
    outer_table = table.find_element_by_tag_name('table')
    rows = outer_table.find_elements_by_tag_name('tr')

    results = []
    for row in rows:
        if 'trSSR_REGFORM_VW' not in row.get_attribute('id'):
            continue
        try:
            elements = row.find_elements_by_tag_name('td')
            number = elements[1].text.split('\n (')[-1][:-1]
            results.append(number)
        except:
            pass

    print('class numbers: ' + str(results))
    return results


def open_search_classes_results(driver, class_num):
    driver.get('https://caesar.ent.northwestern.edu/psc/CS857PRD/EMPLOYEE/SA/c/SA_LEARNER_SERVICES.CLASS_SEARCH.GBL?pslnkid=NW_SS_SA_CLASS_SEARCH&ICAGTarget=start')
    button = wait(driver, 'DERIVED_CLSRCH_SSR_EXPAND_COLLAPS$149$$1', 10)
    click(driver, button)

    class_field = wait(driver, 'SSR_CLSRCH_WRK_CLASS_NBR$8', 10)
    class_field.send_keys(str(class_num))

    button = wait(driver, 'CLASS_SRCH_WRK2_SSR_PB_CLASS_SRCH', 5)
    click(driver, button)

    button = wait(driver, 'MTG_CLASSNAME$0', 10)
    click(driver, button)


def parse_class_page(driver):
    table = wait(driver, 'ACE_SSR_CLS_DTL_WRK_GROUP3', 10)
    rows = table.find_elements(By.TAG_NAME, "tr")
    results = {}
    for row in rows:
        try:
            elements = row.find_elements(By.TAG_NAME, "td")
            key = elements[1].text.replace('\n', '')
            value = elements[2].text.replace('\n', '')
            results[key] = int(value)
        except:
            pass

    results['title'] = driver.find_element_by_id('DERIVED_CLSRCH_DESCR200').text.replace('\xa0', '')
    results['time'] = driver.find_element_by_id('MTG_SCHED$0').text.replace('\xa0', '')
    return results


driver = webdriver.Safari()
load_cookies(driver)
authenticate_if_needed(driver)
pickle.dump(driver.get_cookies(), open("cookies.pkl", "wb"))

class_numbers = parse_shopping_cart(driver)

results = []
for class_num in class_numbers:
    open_search_classes_results(driver, class_num)
    results.append(parse_class_page(driver))
driver.quit()

print("results:\n")
for class_info in results:
    title = class_info['title']
    time = class_info['time']
    if 'Available Seats' not in class_info:
        print('{} ({}):\nmissing available seats\n'.format(title, time))
        continue

    seats = class_info['Available Seats']
    if 'Class Capacity' in class_info:
        print('{} ({}):\nOpen Seats: {} / {}\n'.format(title, time, seats, class_info['Class Capacity']))
    elif 'Combined Section Capacity' in class_info:
        print('{} ({}):\nOpen Seats: {} / {}\n'.format(title, time, seats, class_info['Combined Section Capacity']))
    else:
        print('{} ({}):\nmissing capacity\n'.format(title, time))
