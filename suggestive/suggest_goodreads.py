from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time


def suggest_goodreads_book_by_projection(book_urls):
    # TODO:
    # - get 5 star ratings for all book urls
    # - get intersection of reviewers
    # - get 5 star ratings for reviewers
    # - present list sorted by most 5 star ratings
    pass


def _get_ratings(book_url, filter_five=False):
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
    return ratings


if __name__ == '__main__':
    url = 'https://www.goodreads.com/book/show/6587879-horns'
    ratings = _get_ratings(url, filter_five=True)
