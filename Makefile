tag:
	git tag ${TAG} -m "${MSG}"
	git push --tags

.python-version:
	@pyenv virtualenv $$(basename ${CURDIR}) > /dev/null 2>&1 || true
	@pyenv local $$(basename ${CURDIR})
	@pyenv version

examples:
	PYTHONPATH=. python examples/generate_hello.py | tee examples/hello.bpmn
	(cd $@; bpmn-to-image hello.bpmn:hello.png)
	PYTHONPATH=. python examples/visitor.py

requirements: .python-version requirements.txt
	@pip install --upgrade -r requirements.txt > /dev/null

upgrade: requirements
	@pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U

test: requirements
	tox

dist: requirements
	rm -rf $@
	python setup.py sdist bdist_wheel

publish-test: dist
	twine upload --repository testpypi dist/*

publish: dist
	twine upload dist/*

coverage: test
	coverage report

docs: requirements
	cd docs; make html
	open docs/_build/html/index.html

PROJECT:=`find . -name '__init__.py' -maxdepth 2 | xargs dirname | grep -v docs`

lint:
	@PYTHONPATH=. pylint ${PROJECT} | tee lint.txt

clean:
	find . -type f -name "*.backup" | xargs rm
	rm -rf build bpmn_tools.egg-info dist

.PHONY: dist docs examples
