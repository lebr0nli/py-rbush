from __future__ import annotations

import math

import rbush


def default_dict_key(item: dict) -> tuple[float, float, float, float]:
    return (item["min_x"], item["min_y"], item["max_x"], item["max_y"])


def assert_sorted_equal(a: list, b: list, key=default_dict_key) -> None:
    assert sorted(a, key=key) == sorted(b, key=key)


def some_data(n: int) -> list[dict[str, float]]:
    return [{"min_x": i, "min_y": i, "max_x": i, "max_y": i} for i in range(n)]


def tuple_to_dict(arr: tuple[float, float, float, float]) -> dict[str, float]:
    return {"min_x": arr[0], "min_y": arr[1], "max_x": arr[2], "max_y": arr[3]}


def tuple_to_bbox(arr: tuple[float, float, float, float]) -> rbush.BBox:
    return rbush.BBox(arr[0], arr[1], arr[2], arr[3])


DATA = list(
    map(
        tuple_to_dict,
        [
            (0, 0, 0, 0),
            (10, 10, 10, 10),
            (20, 20, 20, 20),
            (25, 0, 25, 0),
            (35, 10, 35, 10),
            (45, 20, 45, 20),
            (0, 25, 0, 25),
            (10, 35, 10, 35),
            (20, 45, 20, 45),
            (25, 25, 25, 25),
            (35, 35, 35, 35),
            (45, 45, 45, 45),
            (50, 0, 50, 0),
            (60, 10, 60, 10),
            (70, 20, 70, 20),
            (75, 0, 75, 0),
            (85, 10, 85, 10),
            (95, 20, 95, 20),
            (50, 25, 50, 25),
            (60, 35, 60, 35),
            (70, 45, 70, 45),
            (75, 25, 75, 25),
            (85, 35, 85, 35),
            (95, 45, 95, 45),
            (0, 50, 0, 50),
            (10, 60, 10, 60),
            (20, 70, 20, 70),
            (25, 50, 25, 50),
            (35, 60, 35, 60),
            (45, 70, 45, 70),
            (0, 75, 0, 75),
            (10, 85, 10, 85),
            (20, 95, 20, 95),
            (25, 75, 25, 75),
            (35, 85, 35, 85),
            (45, 95, 45, 95),
            (50, 50, 50, 50),
            (60, 60, 60, 60),
            (70, 70, 70, 70),
            (75, 50, 75, 50),
            (85, 60, 85, 60),
            (95, 70, 95, 70),
            (50, 75, 50, 75),
            (60, 85, 60, 85),
            (70, 95, 70, 95),
            (75, 75, 75, 75),
            (85, 85, 85, 85),
            (95, 95, 95, 95),
        ],
    )
)

EMPTY_DATA = list(
    map(
        tuple_to_dict,
        [
            (-math.inf, -math.inf, math.inf, math.inf),
            (-math.inf, -math.inf, math.inf, math.inf),
            (-math.inf, -math.inf, math.inf, math.inf),
            (-math.inf, -math.inf, math.inf, math.inf),
            (-math.inf, -math.inf, math.inf, math.inf),
            (-math.inf, -math.inf, math.inf, math.inf),
        ],
    )
)


def test_default_max_entries():
    tree = rbush.RBush()
    tree.load(some_data(9))
    result = tree.serialize()
    assert result["root"]["height"] == 1, result

    tree = rbush.RBush()
    tree.load(some_data(10))
    result = tree.serialize()
    assert result["root"]["height"] == 2, result


def test_to_bbox_can_be_overridden_for_custom_data():
    class MyRBush(rbush.RBushBase):
        def to_bbox(self, item: dict) -> rbush.BBox:
            return rbush.BBox(item["min_lng"], item["min_lat"], item["max_lng"], item["max_lat"])

    tree = MyRBush(4)
    data = [
        {"min_lng": -115, "min_lat": 45, "max_lng": -105, "max_lat": 55},
        {"min_lng": 105, "min_lat": 45, "max_lng": 115, "max_lat": 55},
        {"min_lng": 105, "min_lat": -55, "max_lng": 115, "max_lat": -45},
        {"min_lng": -115, "min_lat": -55, "max_lng": -105, "max_lat": -45},
    ]
    tree.load(data)

    def lat_lng_key(item: dict) -> tuple[float, float, float, float]:
        return (item["min_lng"], item["min_lat"], item["max_lng"], item["max_lat"])

    result = tree.search(rbush.BBox(-180, -90, 180, 90))

    assert_sorted_equal(
        result,
        [
            {"min_lng": -115, "min_lat": 45, "max_lng": -105, "max_lat": 55},
            {"min_lng": 105, "min_lat": 45, "max_lng": 115, "max_lat": 55},
            {"min_lng": 105, "min_lat": -55, "max_lng": 115, "max_lat": -45},
            {"min_lng": -115, "min_lat": -55, "max_lng": -105, "max_lat": -45},
        ],
        key=lat_lng_key,
    )

    result = tree.search(rbush.BBox(-180, -90, 0, 90))

    assert_sorted_equal(
        result,
        [
            {"min_lng": -115, "min_lat": 45, "max_lng": -105, "max_lat": 55},
            {"min_lng": -115, "min_lat": -55, "max_lng": -105, "max_lat": -45},
        ],
        key=lat_lng_key,
    )

    result = tree.search(rbush.BBox(0, -90, 180, 90))

    assert_sorted_equal(
        result,
        [
            {"min_lng": 105, "min_lat": 45, "max_lng": 115, "max_lat": 55},
            {"min_lng": 105, "min_lat": -55, "max_lng": 115, "max_lat": -45},
        ],
        key=lat_lng_key,
    )

    result = tree.search(rbush.BBox(-180, 0, 180, 90))

    assert_sorted_equal(
        result,
        [
            {"min_lng": -115, "min_lat": 45, "max_lng": -105, "max_lat": 55},
            {"min_lng": 105, "min_lat": 45, "max_lng": 115, "max_lat": 55},
        ],
        key=lat_lng_key,
    )

    result = tree.search(rbush.BBox(-180, -90, 180, 0))

    assert_sorted_equal(
        result,
        [
            {"min_lng": 105, "min_lat": -55, "max_lng": 115, "max_lat": -45},
            {"min_lng": -115, "min_lat": -55, "max_lng": -105, "max_lat": -45},
        ],
        key=lat_lng_key,
    )


def test_load_sanity():
    tree = rbush.RBush(4)
    tree.load(DATA)
    assert_sorted_equal(tree.all(), DATA)


def test_load_use_standard_insert_when_low_number_of_items():
    tree1 = rbush.RBush(8)
    tree1.load(DATA)
    tree1.load(DATA[:3])

    tree2 = rbush.RBush(8)
    tree2.load(DATA)
    tree2.insert(DATA[0])
    tree2.insert(DATA[1])
    tree2.insert(DATA[2])

    assert tree1.serialize() == tree2.serialize()


def test_load_handle_empty_data():
    tree = rbush.RBush()
    tree.load([])

    assert tree.serialize() == rbush.RBush().serialize()


def test_load_hande_max_entries_plus_two_empty_bboxes():
    tree = rbush.RBush(4)
    tree.load(EMPTY_DATA)

    assert tree.serialize()["root"]["height"] == 2
    assert_sorted_equal(tree.all(), EMPTY_DATA)


def test_insert_handle_max_entries_plus_two_empty_bboxes():
    tree = rbush.RBush(4)

    for data in EMPTY_DATA:
        tree.insert(data)

    assert tree.serialize()["root"]["height"] == 2
    assert_sorted_equal(tree.all(), EMPTY_DATA)
    assert len(tree.serialize()["root"]["children"][0]["children"]) == 4
    assert len(tree.serialize()["root"]["children"][1]["children"]) == 2


def test_load_properly_splits_tree_root_when_merging_trees_of_the_same_height():
    tree = rbush.RBush(4)
    tree.load(DATA)
    tree.load(DATA)

    assert tree.serialize()["root"]["height"] == 4
    assert_sorted_equal(tree.all(), DATA + DATA)


def test_load_properly_merges_data_of_smaller_or_bigger_tree_heights():
    smaller = some_data(10)

    tree1 = rbush.RBush(4)
    tree1.load(DATA)
    tree1.load(smaller)
    tree2 = rbush.RBush(4)
    tree2.load(smaller)
    tree2.load(DATA)

    assert tree1.serialize()["root"]["height"] == tree2.serialize()["root"]["height"]

    assert_sorted_equal(tree1.all(), DATA + smaller)
    assert_sorted_equal(tree2.all(), DATA + smaller)


def test_search_finds_matching_points_in_the_tree_given_a_bbox():
    tree = rbush.RBush(4)
    tree.load(DATA)
    result = tree.search(rbush.BBox(40, 20, 80, 70))

    assert_sorted_equal(
        result,
        list(
            map(
                tuple_to_dict,
                [
                    (70, 20, 70, 20),
                    (75, 25, 75, 25),
                    (45, 45, 45, 45),
                    (50, 50, 50, 50),
                    (60, 60, 60, 60),
                    (70, 70, 70, 70),
                    (45, 20, 45, 20),
                    (45, 70, 45, 70),
                    (75, 50, 75, 50),
                    (50, 25, 50, 25),
                    (60, 35, 60, 35),
                    (70, 45, 70, 45),
                ],
            )
        ),
    )


def test_collides_returns_true_when_search_finds_matching_points():
    tree = rbush.RBush(4)
    tree.load(DATA)

    result = tree.collides(rbush.BBox(40, 20, 80, 70))
    assert result


def test_search_returns_an_empty_array_if_nothing_found():
    tree = rbush.RBush(4)
    tree.load(DATA)
    result = tree.search(rbush.BBox(200, 200, 210, 210))
    assert result == []


def test_collides_returns_false_if_nothing_found():
    tree = rbush.RBush(4)
    tree.load(DATA)
    result = tree.collides(rbush.BBox(200, 200, 210, 210))
    assert not result


def test_all_returns_all_items_in_the_tree():
    tree = rbush.RBush(4)
    tree.load(DATA)

    assert_sorted_equal(tree.all(), DATA)
    assert_sorted_equal(tree.search(rbush.BBox(0, 0, 100, 100)), DATA)


def test_serialize_and_deserialize_exports_and_imports_search_tree_in_JSON_format():
    tree = rbush.RBush(4)
    tree.load(DATA)
    tree2 = rbush.RBush(4)
    tree2.deserialize(tree.serialize())

    assert_sorted_equal(tree.all(), tree2.all())


def test_insert_adds_an_item_to_an_existing_tree_correctly():
    items = list(
        map(tuple_to_dict, [(0, 0, 0, 0), (1, 1, 1, 1), (2, 2, 2, 2), (3, 3, 3, 3), (1, 1, 2, 2)])
    )

    tree = rbush.RBush(4)
    tree.load(items[:3])

    tree.insert(items[3])
    assert tree.serialize()["root"]["height"] == 1
    assert_sorted_equal(tree.all(), items[:4])

    tree.insert(items[4])
    assert tree.serialize()["root"]["height"] == 2
    assert_sorted_equal(tree.all(), items)


def test_insert_forms_a_valid_tree_if_items_are_inserted_one_by_one():
    tree = rbush.RBush(4)

    for i in range(len(DATA)):
        tree.insert(DATA[i])

    tree2 = rbush.RBush(4)
    tree2.load(DATA)

    assert tree.serialize()["root"]["height"] - tree2.serialize()["root"]["height"] <= 1
    assert_sorted_equal(tree.all(), tree2.all())


def test_remove_removes_items_correctly():
    tree = rbush.RBush(4)
    tree.load(DATA)

    length = len(DATA)

    tree.remove(DATA[0])
    tree.remove(DATA[1])
    tree.remove(DATA[2])

    tree.remove(DATA[length - 1])
    tree.remove(DATA[length - 2])
    tree.remove(DATA[length - 3])

    assert_sorted_equal(DATA[3 : length - 3], tree.all())


def test_remove_does_nothing_if_nothing_found():
    tree1 = rbush.RBush(4)
    tree1.load(DATA)
    tree2 = rbush.RBush(4)
    tree2.load(DATA)
    tree2.remove(tuple_to_dict((13, 13, 13, 13)))

    assert_sorted_equal(tree1.all(), tree2.all())


def test_remove_brings_the_tree_to_a_clear_state_when_removing_everything_one_by_one():
    tree = rbush.RBush(4)
    tree.load(DATA)

    for i in range(len(DATA)):
        tree.remove(DATA[i])

    assert tree.serialize() == rbush.RBush(4).serialize()


def test_remove_accepts_an_equals_function():
    tree = rbush.RBush(4)
    tree.load(DATA)

    item = {"min_x": 20, "min_y": 70, "max_x": 20, "max_y": 70, "foo": "bar"}
    copied_item = item.copy()
    assert id(item) != id(copied_item)

    tree.insert(item)
    tree.remove(copied_item, lambda a, b: a.get("foo") == b.get("foo"))

    assert_sorted_equal(tree.all(), DATA)


def test_clear_should_clear_all_the_data_in_the_tree():
    tree = rbush.RBush(4)
    tree.load(DATA)
    tree.clear()
    assert tree.serialize() == rbush.RBush(4).serialize()
