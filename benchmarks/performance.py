from __future__ import annotations

import math
import random
import time

from rbush import BBox
from rbush import RBush

N = 1_000_000
max_fill = 16

print(f"number: {N}")
print(f"maxFill: {max_fill}")


def rand_bbox_dict(size: float) -> dict[str, float]:
    x = random.uniform(0, 100 - size)
    y = random.uniform(0, 100 - size)
    return {
        "min_x": x,
        "min_y": y,
        "max_x": x + size * random.random(),
        "max_y": y + size * random.random(),
    }


def gen_data(n: int, size: float) -> list[dict]:
    return [rand_bbox_dict(size) for _ in range(n)]


def to_bbox(item) -> BBox:
    return BBox(item["min_x"], item["min_y"], item["max_x"], item["max_y"])


# Generate data for insertion
data = gen_data(N, 1)
data2 = gen_data(N, 1)
bbox_100 = list(map(to_bbox, gen_data(1000, 100 * math.sqrt(0.1))))
bbox_10 = list(map(to_bbox, gen_data(1000, 10)))
bbox_1 = list(map(to_bbox, gen_data(1000, 1)))

# Initialize the tree with a maximum fill capacity
tree = RBush(max_fill)

# Benchmark: Insert items one by one
start_time = time.time()
for item in data:
    tree.insert(item)
end_time = time.time()

print(f"Insert {N} items one by one: {end_time - start_time:.2f} seconds")

# Benchmark: Search 1000 items with 10% overlap
start_time = time.time()
for i in range(1000):
    tree.search(bbox_100[i])
end_time = time.time()

print(f"Search 1000 items with 10% overlap: {end_time - start_time:.2f} seconds")

# Benchmark: Search 1000 items with 1% overlap
start_time = time.time()
for i in range(1000):
    tree.search(bbox_10[i])
end_time = time.time()

print(f"Search 1000 items with 1% overlap: {end_time - start_time:.2f} seconds")

# Benchmark: Search 1000 items with 0.01% overlap
start_time = time.time()
for i in range(1000):
    tree.search(bbox_1[i])
end_time = time.time()

print(f"Search 1000 items with 0.01% overlap: {end_time - start_time:.2f} seconds")


# Benchmark: Remove 1000 items one by one
start_time = time.time()
for i in range(1000):
    tree.remove(data[i])
end_time = time.time()

print(f"Remove 1000 items one by one: {end_time - start_time:.2f} seconds")

# Benchmark: Bulk-insert 1,000,000 more items
start_time = time.time()
tree.load(data2)
end_time = time.time()

print(f"Bulk-insert {N} items more: {end_time - start_time:.2f} seconds")
