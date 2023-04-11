from .suggest_utils import _scroll_all, _scroll_to_elem, _scroll_to_end, \
    _get_page_version_banner
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import geckodriver_autoinstaller
from bs4 import BeautifulSoup
import numpy as np
import time
import os
import pickle


def suggest_goodreads_book_by_projection(book_urls, output_fn=None):
    common_reviewers = _get_projection(book_urls)

    books = []
    n_reviewers = 0
    for rr in common_reviewers:
        books.append(_get_books(rr, filter_five=True))
        if len(books[-1]) > 0:
            n_reviewers += 1

    nn = {}
    aa = {}
    for ii, rr in enumerate(common_reviewers):
        for bb in books[ii]:
            if bb in nn:
                nn[bb] += 1
            else:
                nn[bb] = 1
                aa[bb] = books[ii][bb][1]

    ss = []
    tt = []
    ll = []
    for bb in nn:
        if nn[bb] > 1:
            ss.append(nn[bb])
            tt.append(bb)
            ll.append(aa[bb])

    idx = np.argsort(-np.asarray(ss))
    if output_fn is None:
        for ii in idx:
            print('{} : {}'.format(ss[ii], tt[ii]))
    else:
        url_pre = 'https://www.goodreads.com/book/show/'
        with open(output_fn, 'w') as f_out:
            f_out.write('<html><body>\n')

            t1 = book_urls[0].split('/')[-1].split('-', 1)[-1]
            t2 = book_urls[1].split('/')[-1].split('-', 1)[-1]
            hh = (f'Book recommendations based on ({n_reviewers}) '
                  'readers who liked '
                  f'<a href="{book_urls[0]}">{t1}</a> and '
                  f'<a href="{book_urls[1]}">{t2}</a><br /><br />\n')
            f_out.write(hh)

            for ii in idx:
                bb = (f'({ss[ii]}) - <a href="{url_pre}{ll[ii]}">{tt[ii]}'
                      '</a><br />\n')
                f_out.write(bb)

            f_out.write('</body></html>\n')

    return common_reviewers, books


def suggest_goodreads_users_by_projection(book_urls):
    pass


def _get_projection(book_urls):
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


def _get_user_book_rating(review):
    score_mapping = {'it was amazing': 5,
                     'really liked it': 4,
                     'liked it': 3,
                     'it was ok': 2,
                     'did not like it': 1}

    book_info = review.find_all(
        'td', class_='field title')[0].find_all('a')[0]
    book_id = book_info['href'].split('/')[-1]
    book_title = book_info['title']
    try:
        tt = review.find_all('td', class_='field rating')[0].find_all(
            'span', class_='staticStars')[0]['title']
        book_rating = score_mapping[tt]
    except Exception:
        book_rating = None

    return book_title, book_id, book_rating


def _user_stop_early(driver):
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    reviews = soup.find_all('tr', class_='bookalike review')
    rr = _get_user_book_rating(reviews[-1])
    if rr[-1] is None:
        return True
    return False


def _get_books(user_id, filter_five=False):
    user_fn = 'cached/users/{}.p'.format(user_id)
    if os.path.isfile(user_fn):
        print('reading result from cache')
        with open(user_fn, 'rb') as f_in:
            books = pickle.load(f_in)
    else:
        driver = webdriver.Chrome(ChromeDriverManager().install())
        books = {}

        url = ('https://www.goodreads.com/review/list/'
               '{}?page=1&sort=rating'.format(user_id))

        driver.get(url)

        retries = 5
        for ii in range(retries):
            _scroll_to_end(driver, _user_stop_early)
            time.sleep(1)

        _scroll_all(driver)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        reviews = soup.find_all('tr', class_='bookalike review')

        for rr in reviews:
            book_title, book_id, book_rating = _get_user_book_rating(rr)
            if book_rating is None:
                break

            books[book_title] = (book_rating, book_id)

        if not os.path.isdir('cached'):
            os.mkdir('cached')
        if not os.path.isdir('cached/users'):
            os.mkdir('cached/users')
        with open(user_fn, 'wb') as f_out:
            pickle.dump(books, f_out)

        driver.quit()

    if filter_five:
        bf = {}
        for bb in books:
            if books[bb][0] == 5:
                bf[bb] = (5, books[bb][1])
        books = bf

    return books


def _get_ratings(book_url, filter_five=False, max_reviews=3000):
    # new version of goodreads book page
    book_id = book_url.split('/')[-1]
    book_fn = book_id
    if filter_five:
        book_fn += '_filtered'
    book_fn = 'cached/books/{}.p'.format(book_fn)
    if os.path.isfile(book_fn):
        print('reading result from cache')
        with open(book_fn, 'rb') as f_in:
            ratings = pickle.load(f_in)
        return ratings

    # driver = webdriver.Chrome(ChromeDriverManager().install())
    geckodriver_autoinstaller.install()
    driver = webdriver.Firefox()

    ratings = {}

    driver.get(book_url)
    # make sure to get new version of site, without page banner
    # while True:
    #     driver.get(book_url)
    #     pn, pb = _get_page_version_banner(driver)
    #     if pn is True:
    #         if pb is False:
    #             break
    #         else:
    #             time.sleep(2)
    #     else:
    #         time.sleep(10)
    #         driver.quit()
    #         driver = webdriver.Chrome(
    #             ChromeDriverManager().install())

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
        except Exception:
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
            time.sleep(4)
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
    if not os.path.isdir('cached/books'):
        os.mkdir('cached/books')
    with open(book_fn, 'wb') as f_out:
        pickle.dump(ratings, f_out)

    return ratings
