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
- [X] Telegraph
- [X] Vice
- [X] Vox
- [X] Daily Beast
- [X] Salon
- [X] New Yorker
- [X] WaPo: Required sending headers form requests, scrapy default headers
  refused, kind of slow but that's okay. I think they don't mind scraping but
  they give it the slow lane
- [ ] US News: Requires headers, has a honey pot
- [ ] Daily Mail: 403s even with headers on all subpages; Can't really use
  selenium unless I figure out the 403 problem or how to handle requests myself
- [ ] Foreign Affairs: Paywall
- [ ] Newsweek: 403
- [ ] Washington Monthly
- [X] Foreign Policy
- [X] MSNBC
- [X] The Intercept
- [X] Vanity Fair
- [X] Tampa Bay Times
- [ ] Orlando Sentinel
- [X] Al Jazeera
- [X] Axios
- [ ] New York Daily News
- [ ] Business Insider
- [ ] MSN News
- [ ] Los Angeles Times
- [ ] New York Post
- [ ] Time
- [ ] SFGate
- [ ] Slate
- [ ] Chron
- [ ] Chicago Tribune
- [ ] The Mirror
- [ ] Independent.co.uk
- [ ] Detroit Free Press
- [ ] Boston Globe
- [ ] Atlantic
- [ ] Boston.com
- [ ] Dallas Morning News
- [X] Daily Wire
- [ ] Jacobin
- [ ] Daily Kos
- [ ] Mother Jones
- [ ] Reuters
- [ ] AP

I'm pulling a lot of ideas from this: https://libguides.wlu.edu/c.php?g=357505&p=2412837

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
