# Makefile for your_project_name

.PHONY: all run test clean

all: install_requirements run

install_requirements:
	pip install -r requirements.txt

run:
	PYTHONPATH=$$PYTHONPATH:$$(pwd) python3 sms_alert_forge/__main__.py --config conf/config.yaml

test:
	PYTHONPATH=$$PYTHONPATH:$$(pwd) pytest -v tests/test_*.py

clean:
	rm -rf logs __pycache__
