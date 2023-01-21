from suggestive.suggest_goodreads import *


if __name__ == '__main__':
    book_urls = ['https://www.goodreads.com/book/show/6587879-horns',
                 'https://www.goodreads.com/book/show/23168277-the-sympathizer']
    oo = suggest_goodreads_book_by_projection(book_urls)
