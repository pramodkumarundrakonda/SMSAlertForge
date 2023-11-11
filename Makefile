# Makefile for your_project_name

.PHONY: all run test clean

all: install_requirements run

install_requirements:
	pip install -r requirements.txt

run:
	python3 src/__main__.py --config conf/config.yaml

test:
	pytest tests/test_*.py

clean:
	rm -rf logs __pycache__
