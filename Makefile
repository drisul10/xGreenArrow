install-deps:
	pip3 install requests pandas matplotlib schedule

fetch:
	python3 script/data_fetcher.py

analyze:
	python3 script/data_analyzer.py

team-watch:
	python3 script/team_watcher.py

preseason-recommender:
	python3 script/transfer_preseason_recommender.py

recommender:
	python3 script/transfer_recommender.py

manager:
	python3 script/manager.py

diagnose:
	python3 script/diagnose.py

clean:
	rm -f fpl_data_*.csv
	rm -f *.png