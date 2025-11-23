SHELL := bash
.ONESHELL:
.SHELLFLAGS := -eu -o pipefail -c
.DELETE_ON_ERROR:
MAKEFLAGS += --warn-undefined-variables
MAKEFLAGS += --no-builtin-rules

ifeq ($(origin .RECIPEPREFIX), undefined)
  $(error This Make does not support .RECIPEPREFIX. Please use GNU Make 4.0 or later)
endif
.RECIPEPREFIX = >
# all the above taken from https://tech.davis-hansson.com/p/make/

.PHONY: install 
install:
> uv sync

.PHONY: run
run:
> uv run python -m http.server 9000 --directory out/

.PHONY: fmt 
fmt: 
> uv run djlint src/**/*.html --reformat

.PHONY: build
build:
> uv run build.py

.PHONY: build-all
build-all:
> CF_PAGES=true uv run build.py

.PHONY: purge 
purge: 
> rm -rf ./out && mkdir out