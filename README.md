# Maudlin

Maudlin is a news spider cum sentiment analysis database cum web-based
dashboard. I started this project just to learn how to use Scrapy, and it
spiraled from there.

There are currently 41 scrapers for most of the major news sites, and some more
partisan sources, as well as a few local news sources (I prefer high quality
sources, like Tampa Bay Times, not syndicated-style local sources like Bay News
9).

These scrapers run on a local server at my house and deposit the articles, with
a sentiment/positivity score calculated using NLTK/Vader_Sentiment, into a
Postgres db on Digital Ocean.

The dashboard is viewable at [maudlin.standingwater.io][0].

## Installation/Development

To locally install the system, just install the dependencies, create a postgres
database, define stuff in `scrapy.cfg` and `.env` (templates provided), and it
should just work.

To run any scraper, just run `scrapy crawl <scrapername>`.

Beyond that, you can ask me or read up on how scrapy and flask work.

## Types of News Sources

Right now I'm just dealing with American News. Perhaps at some point I'll branch
out, but for now I think that'll do. I'd like to add more local news sources as
well.

## Scraping Targets

I focus on just getting the front page articles for every news organization.
Initially I thought of spidering the entire site but I decided that's way more
work and way too much data, so instead I just get the front page every hour and
only scrape articles I don't have yet.

## Dashboard

- [ ] Sentiment over time graphs for each agency
- [ ] Partisanship weighted daily sentiment
  - If I find a partisanship number this shouldn't be too hard.
- [ ] Compare sentiment on a given story across agencies and articles
  - Okay, this will be the most difficult thing I've thought of: basically, if I
    can identify articles that focus on the same subject (e.g., the Jan. 6
    insurrection) I can score how the subject is portrayed across agencies
  - How To: I can try this algorithm:
    - For any two articles:
    - Tokenize the articles
    - Remove useless words (based on nltk Parts of Speech). I really just want
      nouns
    - Normalize the words to their principle forms (e.g., running to run or
      Republicans to republican)
    - Score the similarity between the lists of words (see:
      https://blogs.oracle.com/meena/finding-similarity-between-text-documents
      and
      https://stackoverflow.com/questions/14720324/compute-the-similarity-between-two-lists/14720386)
  - I do not know what kinds of scores this will produce, nor do I know how
    accurate the similarity score it produces will be. If it seems accurate,
    then I'll be on the road to story partisanship scores.
  - This is a really exciting idea. It will require running a crontab
    asynchronous task because there's no way I can score articles upon creation.
    The combinatorial explosion would be insane. Also, I'll need to limit it to
    certain time periods.
  - One possibility is to manually create a "Story" which identifies a subject
    and scores articles. The "story" can have a start date and a duration for
    scoring because, for instance, I see multiple articles talking about an
    Iraqi bomb today, but that won't last long, whereas the Jan. 6 Insurrection
    is still getting articles today five months later.

[0]: https://maudlin.standingwater.io
