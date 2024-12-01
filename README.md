# py-rbush

This is a Python port of the JavaScript library, [mourner/rbush](https://github.com/mourner/rbush). 

RBush is a high-performance JavaScript library for 2D **spatial indexing** of points and rectangles.
It's based on an optimized **R-tree** data structure with **bulk insertion** support.

*Spatial index* is a special data structure for points and rectangles
that allows you to perform queries like "all items within this bounding box" very efficiently
(e.g. hundreds of times faster than looping over all items).
It's most commonly used in maps and data visualizations.

## Installation

1. Instead of writing the entire library in Python, we implemented the core functionality in C++ and used [pybind11](https://github.com/pybind/pybind11) for better performance. So make sure you have a C++ compiler (e.g. `g++` or `clang++`) available in your environment.
2. Make sure you have `git` installed in your environment.
3. Install the package using pip:
```shell
pip install git+https://github.com/lebr0nli/py-rbush.git
```

## Performance

We used the same way to benchmark the performance as the [original](https://github.com/mourner/rbush/blob/main/bench/perf.js) JavaScript RBush. Check [performance.py](<./benchmarks/performance.py>) for more details.

The following tables are the results of the performance test with Python 3.10 on an 8-core M1 CPU.

- Comparison with another Python port of RBush (but written in pure Python)

Test                         | RBush  | [pure Python RBush](https://github.com/parietal-io/py-rbush) | Improvement
---------------------------- | ------ | ------ | ----
insert 1M items one by one   | 1.03s  | 51.67s | 50.2x
1000 searches of 0.01% area  | 0.01s  | 2.90s  | 290.0x
1000 searches of 1% area     | 0.13s  | 9.03s  | 69.5x
1000 searches of 10% area    | 0.92s  | 42.02s | 45.7x
remove 1000 items one by one | 0.006s | 1.42s  | 236.7x
bulk-insert 1M items         | 0.44s  | 17.01s | 38.7x

- Comparison with the original JavaScript RBush

Test                         | RBush  | [JavaScript RBush](https://github.com/mourner/rbush) | Improvement
---------------------------- | ------ | ------ | ----
insert 1M items one by one   | 1.03s  | 1.13s  | 1.0x
1000 searches of 0.01% area  | 0.01s  | 0.03s  | 3.0x
1000 searches of 1% area     | 0.13s  | 0.30s  | 2.3x
1000 searches of 10% area    | 0.92s  | 1.28s  | 1.4x
remove 1000 items one by one | 0.005s | 0.009s | 1.8x
bulk-insert 1M items         | 0.44s  | 1.06s  | 2.4x

> [!NOTE]
> Most of the runtime is spent on the Python side rather than the C++ side, so the performance improvement will be more significant when the number of items is large.

## Usage guide

Check out the [user guide](https://lebr0nli.github.io/py-rbush/user_guide/) for detailed usage instructions.

## Developer guide

Check out the [developer guide](https://lebr0nli.github.io/py-rbush/developer_guide/) for instructions on building, testing, and linting the project.

## Upstream

This library is a straight-up port of several JavaScript libraries written by Vladimir Agafonkin:

- [RBush 4.0.1](https://github.com/mourner/rbush)
- [QuickSelect 3.0.0](https://github.com/mourner/quickselect)

All of these are published under MIT or ISC licenses.
