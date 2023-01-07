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


def _get_ratings(book_url, filter_five=False):
    book_id = book_url.split('/')[-1]
    book_fn = book_id
    if filter_five:
        book_fn += 'filtered'
    book_fn = 'cached/{}.p'.format(book_fn)
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


if __name__ == '__main__':
    book_urls = ['https://www.goodreads.com/book/show/6587879-horns',
                 'https://www.goodreads.com/book/show/23168277-the-sympathizer']
    oo = suggest_goodreads_book_by_projection(book_urls)
