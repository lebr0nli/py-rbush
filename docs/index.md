# Introduction

This is a Python port of the original JavaScript library, [mourner/rbush](https://github.com/mourner/rbush). 

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
