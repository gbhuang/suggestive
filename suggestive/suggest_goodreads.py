from .suggest_utils import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import os
import pickle


def suggest_goodreads_book_by_projection(book_urls):
    # TODO:
    # - get 5 star ratings for reviewers
    # - present list sorted by most 5 star ratings

    all_ratings = []
    for book_url in book_urls:
        all_ratings.append(_get_ratings(book_url, filter_five=True))

    common_reviewers = all_ratings[0].keys()
    print('initial num reviewers: {}'.format(len(common_reviewers)))

    for ii in range(1, len(all_ratings)):
        common_reviewers = common_reviewers & all_ratings[ii].keys()
        print('n_books = {}, num reviewers: {}'.format(
            ii, len(common_reviewers)))

    return common_reviewers


def _get_ratings(book_url, filter_five=False, max_reviews=6000):
    # new version of goodreads book page
    book_id = book_url.split('/')[-1]
    book_fn = book_id
    if filter_five:
        book_fn += '_filtered'
    book_fn = 'cached/{}.p'.format(book_fn)
    if os.path.isfile(book_fn):
        print('reading result from cache')
        with open(book_fn, 'rb') as f_in:
            ratings = pickle.load(f_in)
        return ratings

    driver = webdriver.Chrome(ChromeDriverManager().install())

    ratings = {}

    # make sure to get new version of site, without page banner
    while True:
        driver.get(book_url)
        pn, pb = _get_page_version_banner(driver)
        if pn is True:
            if pb is False:
                break
            else:
                time.sleep(2)
        else:
            time.sleep(10)
            driver.quit()
            driver = webdriver.Chrome(
                ChromeDriverManager().install())

    # click through to reviews page
    _scroll_to_end(driver)
    aa = driver.find_element_by_css_selector(
        '[aria-label="Tap to show more reviews and ratings"]')
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(1)
    _scroll_to_elem(driver, aa, click=True)

    # first clear any set filters
    while True:
        try:
            aa = driver.find_element_by_css_selector(
                '[aria-pressed="true"]')
            print('clicking to clear filter')
            _scroll_to_elem(driver, aa, click=True)
            time.sleep(4)
        except:
            break

    if filter_five:
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(1)
        aa = driver.find_element_by_css_selector(
            '[aria-label="5 stars"]')
        _scroll_to_elem(driver, aa, click=True)
        time.sleep(4)

    n_reviews = 30
    n_fail = 0
    while n_reviews < max_reviews:
        try:
            aa = driver.find_element_by_css_selector(
                '[data-testid="loadMore"]')
            _scroll_to_elem(driver, aa, click=True)
            n_reviews += 30
            n_fail = 0
            time.sleep(3)
        except Exception as e:
            print(e)
            n_fail += 1
            driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(5)
        if n_fail == 3:
            break

    _scroll_to_end(driver)
    _scroll_all(driver)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    reviews = soup.find_all('article', class_='ReviewCard')

    for review in reviews:
        score = review.find_all('span', class_='RatingStars')[0]
        score = int(score['aria-label'][7])
        user = review.find_all('div', class_='ReviewerProfile__name')[0]
        user = user.find_all('a')[0]['href'].split('/')[-1]
        ratings[user] = score

    # TODO: left below commented out for debugging purposes
    # driver.quit()

    if not os.path.isdir('cached'):
        os.mkdir('cached')
    with open(book_fn, 'wb') as f_out:
        pickle.dump(ratings, f_out)

    return ratings
