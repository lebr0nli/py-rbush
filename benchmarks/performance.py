from __future__ import annotations

import math
import random
import time
from functools import wraps

from rbush import BBox
from rbush import RBush

try:
    import rbush.debug as dbg

    DEBUG_ENABLED = True
except NotImplementedError:
    DEBUG_ENABLED = False

# Constants
NUM_ITEMS = 1_000_000
MAX_FILL = 16
SEARCH_COUNT = 1000
REMOVE_COUNT = 1000


def benchmark(description: str, cpp_lookup_method: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if DEBUG_ENABLED:
                cpp_time_before = dbg.get_total_time(cpp_lookup_method)
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            elapsed_time = end_time - start_time
            if DEBUG_ENABLED:
                print(f"{description} (total): {elapsed_time:.2f} seconds")
                cpp_time_after = dbg.get_total_time(cpp_lookup_method) - cpp_time_before
                print(f"{description} (C++): {cpp_time_after:.2f} ms")
            else:
                print(f"{description}: {elapsed_time:.2f} seconds")
            print()
            return result

        return wrapper

    return decorator


# Helper functions
def rand_dict(size: float) -> dict[str, float]:
    x = random.random() * (100 - size)
    y = random.random() * (100 - size)
    return {
        "min_x": x,
        "min_y": y,
        "max_x": x + size * random.random(),
        "max_y": y + size * random.random(),
    }


def gen_data(n: int, size: float) -> list[dict[str, float]]:
    return [rand_dict(size) for _ in range(n)]


def to_bbox(item: dict[str, float]) -> BBox:
    return BBox(item["min_x"], item["min_y"], item["max_x"], item["max_y"])


@benchmark(f"Insert {NUM_ITEMS} items one by one", "insert")
def insert_data(tree: RBush) -> None:
    for item in DATA:
        tree.insert(item)


@benchmark(f"Search {SEARCH_COUNT} items with 10% overlap", "search")
def search_bbox100(tree: RBush) -> None:
    for box in BBOX_100:
        tree.search(box)


@benchmark(f"Search {SEARCH_COUNT} items with 1% overlap", "search")
def search_bbox10(tree: RBush) -> None:
    for box in BBOX_10:
        tree.search(box)


@benchmark(f"Search {SEARCH_COUNT} items with 0.01% overlap", "search")
def search_bbox1(tree: RBush) -> None:
    for box in BBOX_1:
        tree.search(box)


@benchmark(f"Remove {REMOVE_COUNT} items one by one", "remove")
def remove_data(tree: RBush) -> None:
    for i in range(REMOVE_COUNT):
        tree.remove(DATA[i])


@benchmark(f"Bulk insert {NUM_ITEMS} items more items", "load")
def bulk_insert_data2(tree: RBush) -> None:
    tree.load(DATA2)


@benchmark(f"Search {SEARCH_COUNT} items with 1% overlap again", "search")
def search_bbox10_again(tree: RBush) -> None:
    for box in BBOX_10:
        tree.search(box)


@benchmark(f"Search {SEARCH_COUNT} items with 0.01% overlap again", "search")
def search_bbox1_again(tree: RBush) -> None:
    for box in BBOX_1:
        tree.search(box)


def main():
    print(f"Number of items: {NUM_ITEMS}")
    print(f"Max fill: {MAX_FILL}")
    print()

    tree = RBush(MAX_FILL)

    insert_data(tree)
    search_bbox100(tree)
    search_bbox10(tree)
    search_bbox1(tree)
    remove_data(tree)
    bulk_insert_data2(tree)
    search_bbox10_again(tree)
    search_bbox1_again(tree)


if __name__ == "__main__":
    DATA = gen_data(NUM_ITEMS, 1)
    DATA2 = gen_data(NUM_ITEMS, 1)
    BBOX_100 = list(map(to_bbox, gen_data(SEARCH_COUNT, 100 * math.sqrt(0.1))))
    BBOX_10 = list(map(to_bbox, gen_data(SEARCH_COUNT, 10)))
    BBOX_1 = list(map(to_bbox, gen_data(SEARCH_COUNT, 1)))
    main()
