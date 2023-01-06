import requests
from bs4 import BeautifulSoup


def get_ratings(book_url):
    score_mapping = {'it was amazing': 5,
                     'really liked it': 4,
                     'liked it': 3,
                     'it was ok': 2,
                     'did not like it': 1}

    ratings = {}
    response = requests.get(book_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    reviews = soup.find_all('div', class_='review')

    for review in reviews:
        score = review.find_all('span', class_='staticStars')
        score = score_mapping[score[0]['title']]
        user = review.find_all('a', class_='user')[0][
            'href'].split('/')[-1]
        ratings[user] = score

    return ratings


if __name__ == '__main__':
    url = 'https://www.goodreads.com/book/show/6587879-horns'
    ratings = get_ratings(url)
