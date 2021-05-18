start:
	sudo systemctl start postgresql;\
		sudo systemctl start redis;
run:
	FLASK_ENV=development flask run
freeze:
	pip freeze | sed 's|scrapyd-client.*$$|git+https://github.com/malan88/scrapyd-client/|g' > requirements.txt
celery:
	celery -A newscrawler.tasks worker -B --without-gossip --without-mingle --without-heartbeat -l INFO
celerydebug:
	celery -A newscrawler.tasks worker -B -l DEBUG
