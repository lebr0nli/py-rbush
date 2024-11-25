POETRY := poetry
RUFF := $(POETRY) run ruff
PYTEST := $(POETRY) run pytest
CLANG_FORMAT := clang-format

CPP_SRC_DIR := _rbush
CPP_SRC_FILES := $(shell find $(CPP_SRC_DIR) -name '*.cpp' -o -name '*.h' -o -name '*.cc')
BENCHMARK_SCRIPT := benchmarks/performance.py
TESTS_DIR := tests

.PHONY: install dev-install lint lint-python lint-cpp fix fix-python fix-cpp test bench clean update-submodules

install: update-submodules
	$(POETRY) install

dev-install: update-submodules
	$(POETRY) install -v --with dev

update-submodules:
	git submodule update --init --recursive

lint: lint-python lint-cpp

lint-python:
	$(RUFF) check
	$(RUFF) format --diff

lint-cpp:
	$(CLANG_FORMAT) --dry-run --Werror $(CPP_SRC_FILES)

fix: fix-python fix-cpp

fix-python:
	$(RUFF) check --fix
	$(RUFF) format

fix-cpp:
	$(CLANG_FORMAT) -i $(CPP_SRC_FILES)

test:
	$(PYTEST) $(TESTS_DIR) -vvv

bench:
	$(POETRY) run python $(BENCHMARK_SCRIPT)

clean:
	rm -rf __pycache__ build setup.py dist *.so
