POETRY=poetry
RUFF=$(POETRY) run ruff
CLANG_FORMAT=clang-format


CPP_SRC_DIR=_rbush
CPP_SRC_FILES=$(shell find $(CPP_SRC_DIR) -name '*.cpp' -o -name '*.h' -o -name '*.cc')

install_deps:
	$(POETRY) install

lint: lint-python lint-cpp

lint-python: install_deps
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
	$(POETRY) install
	$(POETRY) run pytest -vvv

clean:
	rm -rf __pycache__ build dist *.so

.PHONY: install_deps lint lint-python lint-cpp fix fix-python fix-cpp test clean