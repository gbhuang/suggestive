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
        except:
            page_banner = True
    except:
        page_new = False
        try:
            driver.find_element(By.LINK_TEXT,
                                'More filters').click()
            page_banner = False
        except:
            page_banner = True
    return page_new, page_banner


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
            except:
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
            except:
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


def _scroll_to_end(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
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


if __name__ == '__main__':
    book_urls = ['https://www.goodreads.com/book/show/6587879-horns',
                 'https://www.goodreads.com/book/show/23168277-the-sympathizer']
    oo = suggest_goodreads_book_by_projection(book_urls)
