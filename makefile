#.EXPORT_ALL_VARIABLES
SHELL:=/usr/bin/env bash

PROJECT_NAME ?= zillow_api
PYTHON3_VERSION=$(shell python3 --version | grep -o '3.7')
VENV_DIR='.venv'
TIME_STAMP=$(shell date +"%y%m%d")

ifneq "$(PYTHON3_VERSION)" "3.7"
$(error 'Python 3.7.x is required.')
endif

######################
# Help
######################
.PHONY: help
help:
	@echo 'List all targets with "make list"'
	@echo 'To install run "make install". It''s recommended to run "make createVirtualEnvironment" and enter the virtual environment first.'



######################
# Install Helpers
######################
.PHONY: install
install:
	pip install -r requirements.txt

.PHONY: createVirtualEnvironment
createVirtualEnvironment:
	python3 -m venv --prompt $(PROJECT_NAME) ./$(VENV_DIR)
	@echo 'Environment created. Run "source ./$(VENV_DIR)/bin/activate" to activate the virtual environment.\n"deactivate" to exit it.'

.PHONY: installForLocalDev
installForLocalDev: createVirtualEnvironment
	$(VENV_DIR)/bin/pip install -r requirements.txt
	@echo 'Local install complete'



########################
# Testing & Lint
########################
TESTS_DIR=tests/unit
MIN_TEST_COVERAGE ?= 0
UNIT_TEST_REPORT_COMMON_FLAGS =
COVERAGE_DIR='coverage_data'
TEST_RESULTS_JSON_FILE=/tmp/testResults.json
PYTHONPATH=$(shell echo "`pwd`:$$PYTHONPATH")

.PHONY: test
test: unitTest integrationTests
	@echo 'Testing complete'

.coverage: cleanCoverage
	@PYTHONBREAKPOINT=0 \
	PYTHONPATH=$(PYTHONPATH) \
	coverage run --branch -m unittest discover --verbose --pattern '*_test.py' --start-directory $(TESTS_DIR) --top-level-directory '.'

.PHONY: unitTest
unitTest: .coverage
	@echo

.PHONY: unitTestReport
unitTestReport: .coverage
	@coverage xml -o $(COVERAGE_DIR)/unit_test_coverage.xml
	@coverage html --skip-covered --directory=$(COVERAGE_DIR)/unit_test_coverage_html
	coverage report --skip-covered --show-missing

.PHONY: unitTestFailUnder
unitTestFailUnder: .coverage
	coverage report --fail-under=$(MIN_TEST_COVERAGE) --skip-covered --show-missing 1>/dev/null

.PHONY: unitTestDebug
unitTestDebug:
	PYTHONPATH=$(PYTHONPATH) \
    python -m unittest discover --verbose --pattern '*_test.py' --start-directory $(TESTS_DIR) --top-level-directory '.'

.PHONY: unitTestJSON
unitTestJSON: cleanCoverage
	@PYTHONBREAKPOINT=0 \
	PYTHONPATH=$(PYTHONPATH) \
	coverage run --branch -m tests.utils.unittest.json discover --verbose --pattern '*_test.py' --start-directory $(TESTS_DIR) --top-level-directory '.'

.PHONY: integrationTests
integrationTests:
	@echo 'No integration tests here.'

.PHONY: openReport
openReport: unitTestReport
	open -a "Google Chrome" file://`pwd`/$(COVERAGE_DIR)/unit_test_coverage_html/index.html

.phony: pylint
pylint:
	@echo '###### Pylint #######'
	@find . -type d -name '.venv' -prune -o -type d -name '.git' -prune -o -name '*.py' -print -exec pylint --jobs=0 "{}" +
	@echo '#####################'

.phony: flake8
flake8:
	@echo '###### Flake8 #######'
	@find . -type d -name '.venv' -prune -o -type d -name '.git' -prune -o -name '*.py' -print -exec flake8 --jobs=0 "{}" +
	@echo '#####################'

.PHONY: lint
lint: pylint flake8
	@echo 'Linting with Flake8 and Pylint complete'



##########################
# Clean up
##########################
.PHONY: cleanPyc
cleanPyc:
	@echo 'Cleaning pyc files...'
	@find ./ -name "*.pyc" -delete

.PHONY: cleanPyCache
cleanPyCache:
	@echo 'Cleaning __pycache__ files...'
	@find ./ -name "__pycache__" -type d -delete

.PHONY: cleanCoverage
cleanCoverage:
	@echo 'Cleaning coverage files...'
	@rm -rf $(COVERAGE_DIR)
	@rm -f .coverage

.PHONY: clean
clean: cleanPyc cleanPyCache cleanCoverage
	@echo 'Clean.'



######################
# Help System
######################
.PHONY: list
list:
	@$(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'
