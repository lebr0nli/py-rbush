from __future__ import annotations

import rbush


def assert_list_dict_bbox_equal(a: list[dict[str, float]], b: list[list[float]]):
    sorted_a = sorted([[item["min_x"], item["min_y"], item["max_x"], item["max_y"]] for item in a])
    sorted_b = sorted(b)
    assert sorted_a == sorted_b


def arr_to_dict_bbox(arr) -> dict[str, float]:
    return {"min_x": arr[0], "min_y": arr[1], "max_x": arr[2], "max_y": arr[3]}


def arr_to_bbox(arr) -> rbush.BBox:
    return rbush.BBox(arr[0], arr[1], arr[2], arr[3])


default_data = list(
    map(
        arr_to_dict_bbox,
        [
            [0, 0, 0, 0],
            [10, 10, 10, 10],
            [20, 20, 20, 20],
            [25, 0, 25, 0],
            [35, 10, 35, 10],
            [45, 20, 45, 20],
            [0, 25, 0, 25],
            [10, 35, 10, 35],
            [20, 45, 20, 45],
            [25, 25, 25, 25],
            [35, 35, 35, 35],
            [45, 45, 45, 45],
            [50, 0, 50, 0],
            [60, 10, 60, 10],
            [70, 20, 70, 20],
            [75, 0, 75, 0],
            [85, 10, 85, 10],
            [95, 20, 95, 20],
            [50, 25, 50, 25],
            [60, 35, 60, 35],
            [70, 45, 70, 45],
            [75, 25, 75, 25],
            [85, 35, 85, 35],
            [95, 45, 95, 45],
            [0, 50, 0, 50],
            [10, 60, 10, 60],
            [20, 70, 20, 70],
            [25, 50, 25, 50],
            [35, 60, 35, 60],
            [45, 70, 45, 70],
            [0, 75, 0, 75],
            [10, 85, 10, 85],
            [20, 95, 20, 95],
            [25, 75, 25, 75],
            [35, 85, 35, 85],
            [45, 95, 45, 95],
            [50, 50, 50, 50],
            [60, 60, 60, 60],
            [70, 70, 70, 70],
            [75, 50, 75, 50],
            [85, 60, 85, 60],
            [95, 70, 95, 70],
            [50, 75, 50, 75],
            [60, 85, 60, 85],
            [70, 95, 70, 95],
            [75, 75, 75, 75],
            [85, 85, 85, 85],
            [95, 95, 95, 95],
        ],
    )
)


def test_insert():
    tree = rbush.RBush()
    items = []
    n = 10000
    # TODO: Maybe a more precise way to check all edge cases
    for i in range(n):
        items.append(
            {
                "min_x": i,
                "min_y": i,
                "max_x": i + 1,
                "max_y": i + 1,
            }
        )
        tree.insert(items[i])
    all_items = tree.all()

    # the size and items should be the same
    assert len(all_items) == n
    assert all(item in all_items for item in items)

    # add one item into the tree
    tree.clear()
    item = {"min_x": 42, "min_y": 42, "max_x": 43, "max_y": 43}
    tree.insert(item)
    all_items = tree.all()

    # the size and items should be the same
    assert len(all_items) == 1
    assert all_items[0] == item


def test_inheritance():
    class MyItem:
        def __init__(self, min_x: float, min_y: float, max_x: float, max_y: float) -> None:
            self.min_x = min_x
            self.min_y = min_y
            self.max_x = max_x
            self.max_y = max_y

    class MyRBush(rbush.RBushBase):
        def to_bbox(self, item: MyItem) -> rbush.BBox:
            return rbush.BBox(item.min_x, item.min_y, item.max_x, item.max_y)

    tree = MyRBush()
    item = MyItem(0, 0, 1, 1)
    tree.insert(item)
    all_items = tree.all()
    assert len(all_items) == 1
    assert all_items[0] == item


def test_remove_without_fn():
    tree = rbush.RBush()
    items = []
    n = 500
    for i in range(n):
        items.append(
            {
                "min_x": i,
                "min_y": i,
                "max_x": i + 1,
                "max_y": i + 1,
            }
        )
        tree.insert(items[i])

    assert len(tree.all()) == n

    # remove item from the tree one by one
    for i in range(n):
        tree.remove(items[i])
        all_items = tree.all()
        assert len(all_items) == n - 1 - i
        assert all(item in all_items for item in items[i + 1 :])
        assert items[i] not in all_items


def test_remove_with_fn():
    tree = rbush.RBush()
    items = []
    n = 500
    for i in range(n):
        items.append(
            {
                "min_x": i,
                "min_y": i,
                "max_x": i,
                "max_y": i,
                "data": i,
            }
        )
        tree.insert(items[i])

    assert len(tree.all()) == n

    # remove item from the tree one by one
    for i in range(n):
        # remove without a custom compare function, this should not remove the item
        tree.remove(items[i].copy())
        all_items = tree.all()
        assert len(all_items) == n - i
        assert all(item in all_items for item in items[i:])
        assert items[i] in all_items

        # remove with a custom compare function, this should remove the item even is not the same object
        tree.remove(items[i].copy(), lambda x, y: x["data"] == y["data"])
        all_items = tree.all()
        assert len(all_items) == n - 1 - i
        assert all(item in all_items for item in items[i + 1 :])
        assert items[i] not in all_items


def test_search_when_found():
    tree = rbush.RBush(4)
    for item in default_data:
        tree.insert(item)

    result = tree.search(rbush.BBox(40, 20, 80, 70))

    assert_list_dict_bbox_equal(
        result,
        [
            [70, 20, 70, 20],
            [75, 25, 75, 25],
            [45, 45, 45, 45],
            [50, 50, 50, 50],
            [60, 60, 60, 60],
            [70, 70, 70, 70],
            [45, 20, 45, 20],
            [45, 70, 45, 70],
            [75, 50, 75, 50],
            [50, 25, 50, 25],
            [60, 35, 60, 35],
            [70, 45, 70, 45],
        ],
    )


def test_search_when_not_found():
    tree = rbush.RBush(4)
    for item in default_data:
        tree.insert(item)

    result = tree.search(rbush.BBox(200, 200, 210, 210))
    assert result == []


def test_collides_when_found():
    tree = rbush.RBush(4)
    for item in default_data:
        tree.insert(item)

    result = tree.collides(rbush.BBox(40, 20, 80, 70))
    assert result


def test_collides_when_not_found():
    tree = rbush.RBush(4)
    for item in default_data:
        tree.insert(item)

    result = tree.collides(rbush.BBox(200, 200, 210, 210))
    assert not result
