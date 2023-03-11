# suggestive

- [usage](#usage)
- [motivation](#motivation)
- [goal and methodology](#methodology)
- [next ideas](#next)


## <a name="usage"></a> usage

- See [main.py](main.py) for example usage.

- See [examples](examples) for example output, eg [book recommendations for readers who really enjoyed Horns and The Sympathizer](https://gbhuang.github.io/suggestive/examples/horns_sympathizer).

- note: initial version of scraping code was adapted from [goodreads-scraper](https://github.com/maria-antoniak/goodreads-scraper).


## <a name="motivation"></a> motivation

The impetus for this project was a mid-life ~~crisis~~ realization of sorts.  While I have been interested in book reviews and ratings and the information that can be gleaned from them for some time (for instance, a previous project - [shortsf_analysis](https://github.com/gbhuang/shortsf_analysis) - analyzing reading club story ratings), the thought that provided the necessary activation energy for this project was the realization that, under some mild assumptions, I have read about half the books I will ever read in my lifetime.  Put more starkly, assuming a reading rate of roughly a book a month, that leaves a remaining quota of around 500 books.  Each new book I read is then 0.2% of my lifetime allotment of books, which now feels like a weighty commitment to make.

Faced with this finitude, I found myself wishing for a better way of finding books to read, in order to make more optimal use of this limited resource.  One can look through ["best of" lists](https://www.nytimes.com/interactive/2022/11/22/books/notable-books.html), or [recommendations from trusted sources](https://mailchi.mp/joehillfiction/escape-hatch-045-year-end-recommendations), but this feels a little overly reliant on serendipity, and insufficiently systematic, especially as one's personal taste is only factored in at the very end when evaluating the content of such lists.  What unknown and unexpected gems are out there, that might squeeze their way into my list of favorite books, if only there were a more systematic and personalized search tool?

One natural solution to this problem seems to be making use of collaborative filtering, ie the wisdom of the crowds.  For the particular domain of books, there would seem to be large store of useful knowledge embedded in the book ratings available on a site like [goodreads](https://www.goodreads.com/).  For instance, one simple idea I would love to see implemented is to be presented with one's book doppelganger, in other words, the user on goodreads whose set of book ratings is, by some metric, most similar to one's own.  From there, an obvious set of book recommendations are those books that this person has rated highly, that one has not yet read.

Unfortunately, I have no direct access to this full data (and goodreads has also [stopped use of their API](https://www.goodreads.com/api)).  While this rules out certain approaches and interesting ideas, I think, due to the inherent nature of the book recommendation problem, there is still room for generate potentially useful recommendations from just a small, carefully chosen subset of data.  I will briefly discuss the rationale for this next, as well as initial ideas for methodology.

## <a name="methodology"></a> goal and methodology

What is the goal of a book recommendation system?  In the ideal case, such a system would be able to accurately predict how much you will enjoy a given book, and give you recommendations from those books you are predicted to like.  That said, I think, without much loss of detail, the problem can be binarized to predicting whether you will really enjoy reading a given book, or not (as opposed to how much).  As an aside, it is for this reason that I don't really know what to make of numbers like those netflix produces, that a given show is say a 71% match for you.  Does this mean you will enjoy the show to a degree of 71%?  Or that there is a 71% chance you will enjoy the show?  In either case, does that level of detail matter?  I think it would suffice to know the shows that I am highly likely to enjoy, rather than worrying about percentages, particularly those lower than some high threshold of say 90%.

In any case, returning to the question of the goal of a book recommendation system, in the set-up above, where the system returned a list of books, how should that list be evaluated, in terms of accuracy and usefulness?  From personal experience with the above noted alternatives to a recommendation system, I think the bar is fairly low.  Existing sources of book recommendations have one of two problems - either the accuracy is very low, because they are coming from a general or a random source, or the specific suggestions are somewhat obvious and likely already saturated because the information they are keying off of is too limited.  As an example of what I mean for the latter, if someone enjoys reading Stephan King novels, then suggesting other novels by King is of low value, and suggestions such as well-known or well-rated horror novels is of only marginally higher value.

All that said, my modest, and I hope attainable, goal for this project is to produce, for one's given query, a set of book recommendations that contains one or two unexpected finds, that one will really enjoy reading.  To bypass the problem of not having access to the full goodreads data, my plan is to make good use of provided user information to sensibly limit the scope of data that needs to be retrieved.

My first thought for this type of input specifications is the idea of "projections" or initial constraints.  More precisely, as a first stab at this idea, consider the projection defined by one's two favorite books, or perhaps slightly better, one's two favorite books that are not closely connected to one another.  As an example, I am a big fan of [Horns](https://www.goodreads.com/book/show/6587879-horns), arguably somewhat literary-horror-genre fiction, and [The Sympathizer](https://www.goodreads.com/book/show/23168277-the-sympathizer), Asian-American-Pulitzer-winning-literary fiction.  The intersection of the Venn diagram of goodreads reviewers who also strongly enjoy these two books would seem to be a useful and constrained source of information to leverage for other book recommendations.

The above idea is what is coded in the `suggest_goodreads_book_by_projection` function.  First, the common set of reviewers who rated both books as 5 stars is obtained, and then the full set of reviews from each of these reviewers is aggregated together, and the number of 5 star reviews given to each book is tallied up.  As an example of the output, [this set of books](https://gbhuang.github.io/suggestive/examples/horns_sympathizer) is recommended given the inputs mentioned earlier of Horns and The Sympathizer.

## <a name="next"></a> next ideas

There are a number of thoughts on next steps, continuing the reasoning above of using an initial set of projections.  Some ideas toward the top of the queue:

- [ ] re-weighting based on book overall frequency (Harry Potter problem)
- [ ] taking goodreads profile as input, to evaluate set of recommendations
- [ ] taking goodreads profile as input, to re-weight/re-score recommendations
- [ ] using projection idea to find book doppelganger
- [ ] taking into account negative scores from common reviewers
- [ ] filtering out "obvious" recommendations
