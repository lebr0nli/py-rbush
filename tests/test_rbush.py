import rbush


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
