# Developer Guide

## Requirements

- python3 (>=3.8)
- [poetry](https://python-poetry.org)
- g++ or clang++
- clang-format

## Installing Dependencies and Building

### Only runtime dependencies

```
make
```

### With dev dependencies

```
make dev-install
```

!!! note
    You need to install dev dependencies to run tests and linting.

### With docs dependencies

```
make docs-install
```

!!! note
    You need to install docs dependencies to build documentation.

## Testing

```
make test
```

## Linting

### Checking

```
make lint
```

### Auto-fixing

```
make fix
```

### Benchmarking

```
make bench
```

!!! note
    You can build rbush with `RBUSH_DEBUG=1 make` to let the benchmarking script can show the time taken by the C++ implementation.

## Serving Documentation

```
make docs
```

## Cleaning Up

```
make clean
```
