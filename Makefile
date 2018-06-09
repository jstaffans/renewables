all: install test

install: check-env
	pip install -r requirements.txt

test: check-env
	pytest tests

check-env:
ifndef VIRTUAL_ENV
  $(error Not running in virtual environment)
endif

pretty: check-env
	black renewables.py app

notebook: check-env
	jupyter notebook --notebook-dir=notebooks/
