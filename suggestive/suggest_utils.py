from selenium.webdriver.common.by import By
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import os
import pickle


def _test_get_page():
    url = 'https://www.goodreads.com/book/show/6587879-horns'
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get(url)

    page_new, page_banner = _get_page_version_banner(driver)
    return page_new, page_banner


def _get_page_version_banner(driver):
    try:
        elem = driver.find_element_by_css_selector(
            '[aria-label="5 stars"]')
        page_new = True
        try:
            elem.click()
            page_banner = False
        except Exception:
            page_banner = True
    except Exception:
        page_new = False
        try:
            driver.find_element(By.LINK_TEXT,
                                'More filters').click()
            page_banner = False
        except Exception:
            page_banner = True
    return page_new, page_banner


def _scroll_to_end(driver, stop_early=None, check_iter=10):
    last_height = driver.execute_script("return document.body.scrollHeight")
    iter = 0
    while True:
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

        iter += 1
        if (stop_early is not None) and ((iter % check_iter) == 0):
            if stop_early(driver):
                break
    return


def _scroll_to_elem(driver, elem, click=False):
    for ii in range(3):
        driver.execute_script("arguments[0].scrollIntoView();", elem)
        time.sleep(1)
    if click:
        elem.click()
    return


def _scroll_all(driver):
    hh = driver.execute_script("return document.body.scrollHeight")
    for ii in range(0, hh, 1000):
        driver.execute_script("window.scrollTo(0, {});".format(ii))
        time.sleep(0.5)
    return


def _get_ratings_old(book_url, filter_five=False):
    # old version of goodreads book page, limited to 300 ratings
    book_id = book_url.split('/')[-1]
    book_fn = book_id
    if filter_five:
        book_fn += '_filtered'
    book_fn = 'cached/{}_old.p'.format(book_fn)
    if os.path.isfile(book_fn):
        print('reading result from cache')
        with open(book_fn, 'rb') as f_in:
            ratings = pickle.load(f_in)
        return ratings

    score_mapping = {'it was amazing': 5,
                     'really liked it': 4,
                     'liked it': 3,
                     'it was ok': 2,
                     'did not like it': 1}

    driver = webdriver.Chrome(ChromeDriverManager().install())

    ratings = {}
    driver.get(book_url)

    if filter_five:
        clicked = False
        while not clicked:
            try:
                time.sleep(2)
                driver.find_element(By.LINK_TEXT, 'More filters').click()
                clicked = True
            except Exception:
                # sign-in banner blocking, or wrong version of site
                driver.get(book_url)

        time.sleep(2)
        driver.find_element(By.PARTIAL_LINK_TEXT, '5 stars ').click()
        time.sleep(2)

    for ii in range(1, 11):
        if ii > 1:  # advance to next set of reviews
            try:
                driver.find_element(By.LINK_TEXT, str(ii)).click()
                time.sleep(3)
            except Exception:
                break

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        reviews = soup.find_all('div', class_='review')

        for review in reviews:
            score = review.find_all('span', class_='staticStars')
            score = score_mapping[score[0]['title']]
            user = review.find_all('a', class_='user')[0][
                'href'].split('/')[-1]
            ratings[user] = score

    # TODO: left below commented out for debugging purposes
    # driver.quit()

    if not os.path.isdir('cached'):
        os.mkdir('cached')
    with open(book_fn, 'wb') as f_out:
        pickle.dump(ratings, f_out)

    return ratings
