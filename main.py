from suggestive import suggest_goodreads as sg


if __name__ == '__main__':
    book_urls = [
        'https://www.goodreads.com/book/show/6587879-horns',
        'https://www.goodreads.com/book/show/23168277-the-sympathizer']
    oo = sg.suggest_goodreads_book_by_projection(
        book_urls, 'horns_sympathizer.html')
