# Article Crawler

I'm interested in writing some news crawlers and doing sentiment analysis on the
results. Let's see who is the most positive and who is the most negative news.

## News Services

- https://www.cnn.com/
- https://www.bbc.com/
- https://www.foxnews.com/
- https://www.npr.org/

https://libguides.wlu.edu/c.php?g=357505&p=2412837

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

Each site is different. I don't yet have a crawler for CNN or BBC. I think
preference should be given to spiders.

## Dashboard

I want to build a dashboard with visualization of positivity over time and
current top stories and positivity rates. Also current word clouds. I'd like to
data vizualize the news. This shouldn't be too difficult with flask and pandas
and maybe d3.
