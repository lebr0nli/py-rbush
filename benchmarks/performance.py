import random
import time

from rbush import RBush

N = 1_000_000
max_fill = 16

print(f"number: {N}")
print(f"maxFill: {max_fill}")


def rand_box(size):
    x = random.uniform(0, 100 - size)
    y = random.uniform(0, 100 - size)
    return {
        "min_x": x,
        "min_y": y,
        "max_x": x + size * random.random(),
        "max_y": y + size * random.random(),
    }


def gen_data(n, size):
    return [rand_box(size) for _ in range(n)]


# Generate data for insertion
data = gen_data(N, 1)

# Initialize the tree with a maximum fill capacity
tree = RBush(max_fill)

# Benchmark: Insert items one by one
start_time = time.time()
for item in data:
    tree.insert(item)
end_time = time.time()

print(f"Insert {N} items one by one: {end_time - start_time:.2f} seconds")
