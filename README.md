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
- [ ] WaPo (probably pretty difficult)

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

Each agency page has some stats, the top most recent 100 articles, and a word
cloud. I'm quite proud of the word cloud idea, I just wish it was faster. Might
look into caching.

I still want graphs over time.
