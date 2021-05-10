# Article Crawler

I'm interested in writing some news crawlers and doing sentiment analysis on the
results. Let's see who is the most positive and who is the most negative news.

## News Services

- [X] CNN
- [X] ABC
- [X] NBC
- [X] CBS
- [X] FOX
- [X] NPR
- [X] BBC
- [X] NYT
- [X] Politico
- [X] The Hill
- [X] The Guardian
- [X] Slate
- [X] The Blaze
- [X] Breitbart
- [ ] US News (Requires headers, has a honey pot)
- [X] Telegraph
- [X] Vice
- [X] Vox
- [X] Daily Beast
- [X] Salon
- [X] New Yorker
- [X] WaPo (Required sending headers form requests, scrapy default headers
  refused, kind of slow but that's okay. I think they don't mind scraping but
  they give it the slow lane)

I'm pulling a lot of ideas from this: https://libguides.wlu.edu/c.php?g=357505&p=2412837


## Notes

I'm interested in Foreign News as well as different levels of analysis (i.e.,
CNN vs Economist).

I'll start small, with the four listed, then branch out. It would be nice to
have an insane amount of crawlers for an insane amount of news sites.

## Types

In building the first few spiders I've discovered there's really two types for
each website:

1. A crawler
2. A spider

The crawler crawls across the entire site finding new articles through links
within each article. This is sometimes easier than otherwise.

The spider just gets the top articles for the day. I run it every hour with a
crontab. This is sometimes easier than other times.

***UPDATE***: I've abandoned the crawlers. It's too processor intensive for a
ras pi. We might change that down the road. But 15+ crawlers running
continuously plus an hourly 15+ spiders is just too much.

## Dashboard

Dashboard is quite preliminary for now. The main page lists all of today's
articles per news agency. This is going to end up being changed because it's too
much content.

The "compound" number is provided by vader_lexicon but I don't like it. It's too
polarized and I think that's mostly because it's just a likelihood that it's
positive or negative, not a "how positive or negative". So I calculate my own
sentiment by just subtracting negative from positive (as provided by
vader_lexicon).

Each agency page has some stats, the top most recent 100 articles, and a word
cloud. I'm quite proud of the word cloud idea, I just wish it was faster. Might
look into caching.

## TODO
- [ ] Sentiment over time graphs for each agency
- [ ] Partisanship weighted daily sentiment
    - If I find a partisanship number this shouldn't be too hard.
- [ ] Compare sentiment on a given story across agencies and articles
    - Okay, this will be the most difficult thing I've thought of: basically, if
      I can identify articles that focus on the same subject (e.g., the Jan. 6
      insurrection) I can score how the subject is portrayed across agencies
    - How To: I can try this algorithm:
        - For any two articles:
        - Tokenize the articles
        - Remove useless words (based on nltk Parts of Speech). I really just
          want nouns
        - Normalize the words to their principle forms (e.g., running to run or
          Republicans to republican)
        - Score the similarity between the lists of words (see:
          https://blogs.oracle.com/meena/finding-similarity-between-text-documents
          and https://stackoverflow.com/questions/14720324/compute-the-similarity-between-two-lists/14720386)
    - I do not know what kinds of scores this will produce, nor do I know how
      accurate the similarity score it produces will be. If it seems accurate,
      then I'll be on the road to story partisanship scores.
    - This is a really exciting idea. It will require running a crontab
      asynchronous task because there's no way I can score articles upon
      creation. The combinatorial explosion would be insane. Also, I'll need to
      limit it to certain time periods.
    - One possibility is to manually create a "Story" which identifies a subject
      and scores articles. The "story" can have a start date and a duration for
      scoring because, for instance, I see multiple articles talking about an
      Iraqi bomb today, but that won't last long, whereas the Jan. 6
      Insurrection is still getting articles today five months later.
