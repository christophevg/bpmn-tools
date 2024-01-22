# colors

GREEN=\033[0;32m
RED=\033[0;31m
BLUE=\033[0;34m
NC=\033[0m

# test envs

PYTHON_VERSIONS ?= 3.8.12 3.9.18 3.10.13 3.11.5
RUFF_PYTHON_VERSION ?= py38

PROJECT=$(shell basename $(CURDIR))
PACKAGE_NAME=`cat .pypi-template | grep "^package_module_name" | cut -d":" -f2`

RUN_CMD?=python -m $(PACKAGE_NAME)
RUN_ARGS?=

TEST_ENVS=$(addprefix $(PROJECT)-test-,$(PYTHON_VERSIONS))

install: install-env-run install-env-docs install-env-test
	@echo "👷‍♂️ $(BLUE)installing requirements in $(PROJECT)$(NC)"
	pyenv local $(PROJECT)
	pip install -U pip > /dev/null
	pip install -U wheel twine > /dev/null

install-env-run:
	@echo "👷‍♂️ $(BLUE)creating virtual environment $(PROJECT)-run$(NC)"
	pyenv local --unset
	-pyenv virtualenv $(PROJECT)-run > /dev/null
	pyenv local $(PROJECT)-run
	pip install -U pip > /dev/null
	pip install -r requirements.txt > /dev/null
	[ -f requirements.run.txt ] && pip install -r requirements.run.txt > /dev/null || true

install-env-docs:
	@echo "👷‍♂️ $(BLUE)creating virtual environment $(PROJECT)-docs$(NC)"
	pyenv local --unset
	-pyenv virtualenv $(PROJECT)-docs > /dev/null
	pyenv local $(PROJECT)-docs
	pip install -U pip > /dev/null
	pip install -r requirements.docs.txt > /dev/null
	
install-env-test: $(TEST_ENVS)

$(PROJECT)-test-%:
	@echo "👷‍♂️ $(BLUE)creating virtual test environment $@$(NC)"
	pyenv local --unset
	-pyenv virtualenv $* $@ > /dev/null
	pyenv local $@
	pip install -U pip > /dev/null
	pip install -U ruff tox > /dev/null

uninstall: uninstall-envs

uninstall-envs: uninstall-env-test uninstall-env-docs uninstall-env-run env clean-env

uninstall-env-test: $(addprefix uninstall-env-test-,$(PYTHON_VERSIONS))

$(addprefix uninstall-env-test-,$(PYTHON_VERSIONS)) uninstall-env-docs uninstall-env-run: uninstall-env-%:
	@echo "👷‍♂️ $(RED)deleting virtual environment $(PROJECT)-$*$(NC)"
	-pyenv virtualenv-delete $(PROJECT)-$*

clean-env:
	@echo "👷‍♂️ $(RED)deleting all packages from current environment$(NC)"
	pip freeze | cut -d"@" -f1 | cut -d'=' -f1 | xargs pip uninstall -y > /dev/null

upgrade:
	@pip list --outdated | tail +3 | cut -d " " -f 1 | xargs -n1 pip install -U

# env switching

env-%:
	pyenv local $(PROJECT)-$*

env:
	pyenv local $(PROJECT)

env-test:
	pyenv local $(TEST_ENVS)
	
# functional targets

run: env-run
	$(RUN_CMD) $(RUN_ARGS)

test: env-test lint
	tox

coverage: test
	coverage report

lint: env-test
	ruff --select=E9,F63,F7,F82 --target-version=$(RUFF_PYTHON_VERSION) .
	ruff --target-version=$(RUFF_PYTHON_VERSION) .

docs: env-docs
	cd docs; make html
	open docs/_build/html/index.html

# packaging targets

publish-test: env dist
	twine upload --repository testpypi dist/*

publish: env dist
	twine upload dist/*

dist: env dist-clean
	python setup.py sdist bdist_wheel

dist-clean: clean
	rm -rf dist build *.egg-info

clean:
	find . -type f -name "*.backup" | xargs rm

.PHONY: dist docs test

# include optional a personal/local touch

-include Makefile.mak
