run:
	FLASK_ENV=development flask run
freeze:
	pip freeze | sed 's|scrapyd-client.*$$|git+https://github.com/malan88/scrapyd-client/|g' > requirements.txt
