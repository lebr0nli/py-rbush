# User Guide

## Overview

The `rbush` module is an Python binding for a spatial indexing data structure (R-tree) implemented in C++ using pybind11. It provides efficient spatial searching and collision detection capabilities.

## Classes

### BBox

Represents a bounding box with spatial coordinates.

#### Constructor

- `BBox()`: Default constructor
- `BBox(min_x: float, min_y: float, max_x: float, max_y: float)`: Create bbox with specific coordinates

#### Attributes

| Attribute | Type   | Description               |
|-----------|--------|---------------------------|
| `min_x`   | double | Minimum x-coordinate      |
| `min_y`   | double | Minimum y-coordinate      |
| `max_x`   | double | Maximum x-coordinate      |
| `max_y`   | double | Maximum y-coordinate      |

#### Methods

- `area() -> float`: Calculate the area of the bounding box
- `contains(other: BBox) -> bool`: Check if this bbox contains another
- `margin() -> float`: Calculate the perimeter of the bbox
- `enlarged_area(other: BBox) -> float`: Calculate enlarged area when extending to another bbox
- `intersection_area(other: BBox) -> float`: Calculate intersection area with another bbox
- `extend(other: BBox)`: Extend current bbox to include another

### RBush

Specialized R-tree implementation using Python dictionaries.

#### Constructor

- `RBush(max_entries: int = 9)`: Create R-tree with optional max entries per node

#### Methods

- `clear()`: Remove all items from the R-tree
- `insert(item: Dict)`: Insert an item into the R-tree
- `load(items: List[Dict])`: Bulk insert items into the R-tree (faster than inserting one by one if you have lots of items)
- `remove(item: Dict, equals: Optional[Callable] = None)`: Remove an item
- `search(bbox: BBox) -> List[Any]`: Search items within a bounding box
- `collides(bbox: BBox) -> bool`: Check if bbox collides with any stored item
- `all() -> List[Any]`: Retrieve all items
- `serialize() -> Dict[str, Any]`: Serialize the R-tree to a dictionary
- `deserialize(data: Dict[str, Any])`: Deserialize the R-tree from a dictionary
- `to_bbox(item: Dict) -> BBox`: Convert item to its bounding box

### RBushBase

Generic R-tree spatial index implementation that you can override `to_bbox` method to support custom item types.

#### Constructor

- `RBushBase(max_entries: int = 9)`: Create R-tree with optional max entries per node

#### Methods

- `clear()`: Remove all items from the R-tree
- `insert(item: Any)`: Insert an item into the R-tree
- `load(items: List[Any])`: Bulk insert items into the R-tree (faster than inserting one by one if you have lots of items)
- `remove(item: Any, equals: Optional[Callable] = None)`: Remove an item
- `search(bbox: BBox) -> List[Any]`: Search items within a bounding box
- `collides(bbox: BBox) -> bool`: Check if bbox collides with any stored item
- `all() -> List[Any]`: Retrieve all items
- `serialize() -> Dict[str, Any]`: Serialize the R-tree to a dictionary
- `deserialize(data: Dict[str, Any])`: Deserialize the R-tree from a dictionary
- `to_bbox(item: Any) -> BBox`: Convert item to its bounding box

!!! important

    By overriding `to_bbox` method, you can support custom item types in the R-tree, this method must be implemented in the derived class.

## Usage Example

### RBush

```python
import math

from rbush import RBush, BBox

# Create R-tree
tree = RBush()

# Clear all items
tree.clear()

# Insert items
item1 = {"min_x": 0, "min_y": 0, "max_x": 10, "max_y": 10, "id": 1}
item2 = {"min_x": 5, "min_y": 5, "max_x": 15, "max_y": 15, "id": 2}
item3 = {"min_x": 10, "min_y": 10, "max_x": 20, "max_y": 20, "id": 3}
tree.insert(item1)
tree.load([item2, item3])

# Search items
results = tree.search(BBox(-math.inf, -math.inf, math.inf, math.inf))

# Check collision
collides = tree.collides(BBox(0, 0, 1, 1))

# Remove item (default equals function is using object identity)
tree.remove(item1)

# Remove item with custom equals function (don't need to be the same object)
tree.remove(item2.copy(), equals=lambda a, b: a["id"] == b["id"])

# Retrieve all items
all_items = tree.all()

# Serialize the tree to dict
tree_dict = tree.serialize()

# Deserialize the tree from dict
tree.deserialize(tree_dict)
```

### RBushBase

```python
from rbush import RBushBase, BBox

class MyItem:
    def __init__(self, a: float, b: float, c: float, d: float) -> None:
        self.a = a
        self.b = b
        self.c = c
        self.d = d

class MyRBush(RBushBase):
    def to_bbox(self, item: MyItem) -> BBox:
        return BBox(item.a, item.b, item.c, item.d)

# Create R-tree with custom item type
tree = MyRBush()

# Insert custom item
item = MyItem(0, 0, 10, 10)
tree.insert(item)

# And so on...
```
