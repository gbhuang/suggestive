# suggestive

- [usage](#usage)
- [motivation](#motivation)
- [methodology](#methodology)


## <a name="usage"></a> usage

main.py

examples (output)

dependencies, running

note: initial version of scraping code was adapted from [goodreads-scraper](https://github.com/maria-antoniak/goodreads-scraper)


## <a name="motivation"></a> motivation

The impetus for this project was a mid-life crisis of sorts.  While I have been interested in book reviews and ratings and the information that can be gleaned from them for some time (for instance, a previous project - [shortsf_analysis](https://github.com/gbhuang/shortsf_analysis) - analyzing reading club story ratings), the thought that provided the necessary activation energy for this project was the realization that, under some mild assumptions, I have read about half the books I will ever read in my lifetime.  Put more starkly, assuming a reading rate of roughly a book a month, that leaves a remaining quota of about 500 books.  Each book I commit to reading is then 0.2% of my lifetime allotment of books, which now feels like a weighty commitment to make.

Faced with this finitude, I found myself wishing for a better way of finding books to read, in order to make more optimal use of this limited resource.  One can look through ["best of" lists](https://www.nytimes.com/interactive/2022/11/22/books/notable-books.html), or [recommendations from trusted sources](https://mailchi.mp/joehillfiction/escape-hatch-045-year-end-recommendations), but this feels a little overly reliant on serendipity, and insufficiently systematic, especially as one's personal taste is only factored in at the very end when evaluating the content of such lists.  What unknown and unexpected gems are out there, that might squeeze their way into my list of favorite books, if only there were a more systematic and personalized search tool?

One natural solution to this problem seems to be making use of collaborative filtering, ie the wisdom of the crowds.  For the particular domain of books, there would seem to be large store of useful knowledge embedded in the book ratings available on a site like [goodreads](https://www.goodreads.com/).  For instance, one simple idea I would love to see implemented is to be presented with one's book doppelganger, in other words, the user on goodreads whose set of book ratings is, by some metric, most similar to one's own.  From there, an obvious set of book recommendations are those books that this person has rated highly, that one has not yet read.

Unfortunately, I have no direct access to this full data (and goodreads has also [stopped use of their API](https://www.goodreads.com/api)).  While this rules out certain approaches and interesting ideas, I think, due to the inherent nature of the book recommendation problem, there is still room for generate potentially useful recommendations from just a small, carefully chosen subset of data.  I will briefly discuss the rationale for this next, as well as initial ideas for methodology.

## <a name="methodology"></a> goal and methodology

evaluation

evaluation metric

tolerate lower precision, good/useful recall
