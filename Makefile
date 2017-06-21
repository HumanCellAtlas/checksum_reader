SHELL=/bin/bash

constants: hca/api_spec.json

lint:
	./setup.py flake8

test: lint
	coverage run --source=$$(python setup.py --name) -m unittest discover

init_docs:
	cd docs; sphinx-quickstart

docs:
	$(MAKE) -C docs html

install:
	-rm -rf dist
	python setup.py bdist_wheel
	pip install --upgrade dist/*.whl

.PHONY: test release docs

include common.mk
