help:
	@echo "Targets:"
	@echo "    make setuptools"
	@echo "    make install"
	@echo "    make build"
	@echo "    make lint"
	@echo "    make publish"
	@echo "    make bumpversion-major"
	@echo "    make bumpversion-minor"
	@echo "    make bumpversion-patch"

setuptools:
	pip install setuptools wheel twine

install:
	pip install -r requirements.dev.txt

lint:
	pre-commit run --all-files

build:
	python setup.py sdist bdist_wheel

publish:
	twine upload dist/*

bumpversion-major:
	bumpversion major --allow-dirty

bumpversion-minor:
	bumpversion minor

bumpversion-patch:
	bumpversion patch