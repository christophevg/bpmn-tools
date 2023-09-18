tag:
	git tag ${TAG} -m "${MSG}"
	git push --tags

.python-version:
	@pyenv virtualenv $$(basename ${CURDIR}) > /dev/null 2>&1 || true
	@pyenv local $$(basename ${CURDIR})
	@pyenv version

# dependencies targets

requirements: .python-version requirements.txt
	@pip install --upgrade -r requirements.txt > /dev/null

upgrade:
	@pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U

# functional targets

test: lint
	tox

coverage: test
	coverage report

lint:
	ruff --select=E9,F63,F7,F82 --target-version=py37 .
	ruff --target-version=py37 .

docs: requirements
	cd docs; make html
	open docs/_build/html/index.html

# packaging targets

dist: dist-clean
	python setup.py sdist bdist_wheel

dist-clean:
	rm -rf dist build *.egg-info

publish-test: dist
	twine upload --repository testpypi dist/*

publish: dist
	twine upload dist/*

clean:
	find . -type f -name "*.backup" | xargs rm

.PHONY: dist docs

# include optional a personal/local touch

-include Makefile.mak
