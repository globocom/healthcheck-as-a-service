# Copyright 2014 healthcheck-as-a-service authors. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.
#
deps:
	@pip install -r requirements.txt

test-deps:
	@pip install -r test-requirements.txt

clean:
	@find . -name "*.pyc" -delete

test: test-deps clean
	@PYTHONPATH=. py.test -s --cov-report term-missing --cov .
	@flake8 --exclude=lib,lib64,dist --max-line-length 150 .

run: deps
	@honcho start

dist:
	@python ./setup.py sdist upload
