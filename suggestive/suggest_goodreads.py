from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
# import requests
from bs4 import BeautifulSoup

# TODOS:
# - switch to selenium to get html
# - add option to limit to 5 stars
# - add default limit for max number of reviews
# - add code to get more than 30 reviews

def get_ratings(book_url):
    score_mapping = {'it was amazing': 5,
                     'really liked it': 4,
                     'liked it': 3,
                     'it was ok': 2,
                     'did not like it': 1}

    driver = webdriver.Chrome(ChromeDriverManager().install())

    ratings = {}
    # response = requests.get(book_url)
    driver.get(book_url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    reviews = soup.find_all('div', class_='review')

    for review in reviews:
        score = review.find_all('span', class_='staticStars')
        score = score_mapping[score[0]['title']]
        user = review.find_all('a', class_='user')[0][
            'href'].split('/')[-1]
        ratings[user] = score

    driver.quit()
    return ratings


if __name__ == '__main__':
    url = 'https://www.goodreads.com/book/show/6587879-horns'
    ratings = get_ratings(url)
