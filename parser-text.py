import pandas as pd
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


def getTexts(elems):
    return [x.text for x in elems]


def getValues(elems):
    return [x.get_attribute('value') for x in elems]


def parseCatalog(start_url, n_pages):
    cat_df = pd.DataFrame()
    driver = webdriver.Chrome()
    driver.get(start_url)
    action = ActionBuilder(driver)
    action.pointer_action.move_to_location(8, 0)
    action.perform()
    try:
        a = driver.find_element(By.CSS_SELECTOR, ".age_popup_btn--agree")
        if not a.is_displayed():
           wait = WebDriverWait(driver, timeout=100)
           wait.until(lambda d: a.is_displayed())
        a.click()
    except NoSuchElementException:
        pass
    try:
        for p in range(1, n_pages + 1):
            driver.get(start_url + '?PAGEN_1=' + str(p))
            elems = driver.find_elements(By.CSS_SELECTOR, ".product_item_images a")
            links = [elem.get_attribute('href') for elem in elems]
            for link in links:
                driver.get(link)
                try:
                    button = driver.find_element(By.CSS_SELECTOR, ".reviews__show-more-button")
                    if button is not None:
                        button.click()
                except NoSuchElementException:
                    pass
                try:
                    comms = getTexts(driver.find_elements(By.CSS_SELECTOR, ".item_bl_review_txt"))
                    rates = getValues(driver.find_elements(By.CSS_SELECTOR, ".item_bl_review_rating .rate_item:checked"))
                    if len(comms) != len(rates):
                        raise Exception(f'Комментариев: {len(comms)}, рейтингов: {len(rates)}, страница: {link}')
                    cat_df = pd.concat([cat_df, pd.DataFrame({'comment': comms, 'rating': rates})], ignore_index=True)
                except Exception as e:
                    print(e)
                    pass
                try:
                    pages = driver.find_elements(By.CSS_SELECTOR, ".bl_pagination li")[-2].text
                    for i in range(2, int(pages) + 1):
                        comm_url = link + '?PAGEN_1=' + str(i)
                        driver.get(comm_url)
                        comms = getTexts(driver.find_elements(By.CSS_SELECTOR, ".item_bl_review_txt"))
                        rates = getValues(driver.find_elements(By.CSS_SELECTOR, ".item_bl_review_rating .rate_item:checked"))
                        if len(comms) != len(rates):
                            raise Exception(f'Комментариев: {len(comms)}, рейтингов: {len(rates)}, страница: {comm_url}')
                        cat_df = pd.concat([cat_df, pd.DataFrame({'comment': comms, 'rating': rates})], ignore_index=True)
                except IndexError:
                    print(".bl_pagination li :", len(driver.find_elements(By.CSS_SELECTOR, ".bl_pagination li")))
                    pass
                except Exception as e:
                    print(e)
                    pass
        print("-Строк - ", len(cat_df.axes[0]))
        driver.quit()
    except Exception as e:
        print(e)
        pass
    return cat_df



df = pd.DataFrame()
rus_wines = parseCatalog('https://krasnoeibeloe.ru/catalog/__2/', 4)
df = pd.concat([df, rus_wines], ignore_index=True)
imp_wines = parseCatalog('https://krasnoeibeloe.ru/catalog/vino/', 8)
df = pd.concat([df, imp_wines], ignore_index=True)
igr_wines = parseCatalog('https://krasnoeibeloe.ru/catalog/vino_igristoe_shampanskoe/', 4)
df = pd.concat([df, igr_wines], ignore_index=True)
df.to_csv("data_comms.csv", mode = 'w')
print("Строк в итоге - ", len(df.axes[0]))