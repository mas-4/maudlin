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

The site and scrapers are running on a Raspberry Pi 4 in my bedroom right now,
because it's a personal project. This may become prohibitively problematic given
the network's upload speed if people start liking the site. Expect downtime at
that point as I migrate to a real VPS.

All of the code is available in my repo [malan88/news-sentiment-analysis][1].
Feel free to fork or submit pull requests.

For the time being I'm calling the site Maudlin, but not really doing much with
it. The styling is rudimentary because I don't care about it right now.

## A Few More Notes

There are some weird quirks with the sentiment. First, Fox seems more positive
I think because it's advertising heavy. I'd like to work on it's scraper to
eliminate that. But "Click" shows up in its wordcloud specifically because it
appears so often within the text of the article with their advertising.

I've also just flat out seen some scores I disagree with, but I'll have to dig
into the articles more and perhaps investigate tuning the model, if possible.

Also note, neutrality is ***NOT*** a score of journalistic neutrality but
basically a neutral tone. I imagine it's closer to "percentage of document that
are neutral words." The result may be strange, when Breitbart appears at the top
for now of neutrality.

[0]: https://www.nltk.org/_modules/nltk/sentiment/vader.html
[1]: https://github.com/malan88/news-sentiment-analysis
