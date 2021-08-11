# About the site

This site is a personal project to scrape as many news agencies as possible and
do sentiment analysis on them to produce a variety of metrics.

The sentiment analysis is performed using NLTK and [Vader Sentiment][0]. Vader
produces four numbers: positivity, negativity, neutrality, and a compound score
which normalizes the other 3 scores.

I actually kind of dislike the compound score because it's very polarized. I
calculate a fifth score I call sentiment which is just positivity minus
negativity. The result is a bit more gradated than compound, but also closer to
the center of the axis [-100, 100].

The website itself (and the database) have seen a bit of migration over the past
six months. It started on a Raspberry Pi 4 with a 4 terabyte external hard drive
in my bedroom. After I essentially fried the Pi with a memory leak due to never
closing Chromium when running it in headless mode through Selenium, I migrated
to a desktop PC running headless Arch Linux, and thence to a Basic Droplet from
Digital Ocean.

Right now, the site itself, and the Postgres database, are running on the
droplet, while the Spiders are running on that headless Arch PC pointed at the
VPS for connecting to the database. This saves me some processing time on the
VPS.

The wordclouds are also generated on my local server, and archived there, but
pushed via SCP in a crontab to the VPS.

All of the code is available in my repo [mas-4/news-sentiment-analysis][1]. Feel
free to fork or submit pull requests.

For the time being I'm calling the site Maudlin, but not really doing much with
it. The styling is rudimentary because I don't care about it right now.

## A Few More Notes

There are some weird quirks with the sentiment.

First, Fox seems more positive I think because it's advertising heavy. I'd like
to work on its scraper to eliminate that. But "Click" shows up in its wordcloud
specifically because it appears so often within the text of the article with
their advertising. **(Update 8/11/21, I've mitigated this by adding certain stop
words to the wordcloud generator, and I believe fixing the scraper itself)**

I've also just flat out seen some scores I disagree with (a cheerful article
that gets a bad score is not hard to recognize), but I'll have to dig into the
articles more and perhaps investigate tuning the model, if possible.

Also note, neutrality is **_NOT_** a score of journalistic neutrality but
basically a neutral tone. I imagine it's closer to "percentage of document that
are neutral words." The result may seem strange when Breitbart appears at the
top for now of neutrality.

[0]: https://www.nltk.org/_modules/nltk/sentiment/vader.html
[1]: https://github.com/mas-4/news-sentiment-analysis
