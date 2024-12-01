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


def test_split_issue_32():
    """
    See https://github.com/lebr0nli/py-rbush/issues/32
    """
    tree = rbush.RBush(16)

    data = list(
        map(
            tuple_to_dict,
            [
                (98.51205090529908, 29.432796087891944, 98.8983398159477, 30.39180129251106),
                (3.244904776840562, 85.56630452718939, 3.5054687519594148, 86.55148054902081),
                (80.72172697236138, 8.43195394430572, 80.73565058443396, 8.78848293889472),
                (96.82819370943757, 57.89645331425522, 97.53135347858124, 58.83373184140501),
                (88.8162881095185, 72.63896221133226, 89.3566488755267, 72.86895213062044),
                (68.16609589076367, 50.46498136589241, 68.69923134542898, 51.37155186894776),
                (94.79616789633582, 56.580211738055716, 95.69535648357065, 57.09695671147431),
                (16.66607930719589, 85.17405603022017, 16.767666158573213, 85.36319718262673),
                (0.9314345585759056, 81.46540088213875, 1.3539064888216576, 81.75729848012693),
                (43.91216091122522, 94.5834962917428, 44.269148406484824, 95.08980613426415),
                (94.91730706851604, 6.329690351592068, 95.6350858150881, 6.344204438406445),
                (79.4198536802949, 51.043117166322965, 79.63903202350052, 51.570797309998625),
                (49.9903106381618, 40.08213015160266, 50.550330815857535, 40.13877488471124),
                (6.832526244922886, 21.437523762645643, 6.962002330131151, 21.877762479743538),
                (40.131680914632845, 44.1723255673172, 41.01928473084451, 44.282911476135226),
                (62.45260928527483, 70.22618714480168, 63.168857787996615, 70.24878043398508),
                (95.77372677147429, 26.74764015964408, 96.64692665810192, 27.32050171418362),
            ],
        )
    )
    for item in data:
        tree.insert(item)

    expected = {
        "max_entries": 16,
        "min_entries": 7,
        "root": {
            "bbox": {
                "max_x": 98.8983398159477,
                "max_y": 95.08980613426415,
                "min_x": 0.9314345585759056,
                "min_y": 6.329690351592068,
            },
            "children": [
                {
                    "bbox": {
                        "max_x": 50.550330815857535,
                        "max_y": 95.08980613426415,
                        "min_x": 0.9314345585759056,
                        "min_y": 21.437523762645643,
                    },
                    "children": [
                        {
                            "max_x": 1.3539064888216576,
                            "max_y": 81.75729848012693,
                            "min_x": 0.9314345585759056,
                            "min_y": 81.46540088213875,
                        },
                        {
                            "max_x": 3.5054687519594148,
                            "max_y": 86.55148054902081,
                            "min_x": 3.244904776840562,
                            "min_y": 85.56630452718939,
                        },
                        {
                            "max_x": 6.962002330131151,
                            "max_y": 21.877762479743538,
                            "min_x": 6.832526244922886,
                            "min_y": 21.437523762645643,
                        },
                        {
                            "max_x": 16.767666158573213,
                            "max_y": 85.36319718262673,
                            "min_x": 16.66607930719589,
                            "min_y": 85.17405603022017,
                        },
                        {
                            "max_x": 41.01928473084451,
                            "max_y": 44.282911476135226,
                            "min_x": 40.131680914632845,
                            "min_y": 44.1723255673172,
                        },
                        {
                            "max_x": 44.269148406484824,
                            "max_y": 95.08980613426415,
                            "min_x": 43.91216091122522,
                            "min_y": 94.5834962917428,
                        },
                        {
                            "max_x": 50.550330815857535,
                            "max_y": 40.13877488471124,
                            "min_x": 49.9903106381618,
                            "min_y": 40.08213015160266,
                        },
                    ],
                    "height": 1,
                    "is_leaf": True,
                },
                {
                    "bbox": {
                        "max_x": 98.8983398159477,
                        "max_y": 72.86895213062044,
                        "min_x": 62.45260928527483,
                        "min_y": 6.329690351592068,
                    },
                    "children": [
                        {
                            "max_x": 63.168857787996615,
                            "max_y": 70.24878043398508,
                            "min_x": 62.45260928527483,
                            "min_y": 70.22618714480168,
                        },
                        {
                            "max_x": 68.69923134542898,
                            "max_y": 51.37155186894776,
                            "min_x": 68.16609589076367,
                            "min_y": 50.46498136589241,
                        },
                        {
                            "max_x": 79.63903202350052,
                            "max_y": 51.570797309998625,
                            "min_x": 79.4198536802949,
                            "min_y": 51.043117166322965,
                        },
                        {
                            "max_x": 80.73565058443396,
                            "max_y": 8.78848293889472,
                            "min_x": 80.72172697236138,
                            "min_y": 8.43195394430572,
                        },
                        {
                            "max_x": 89.3566488755267,
                            "max_y": 72.86895213062044,
                            "min_x": 88.8162881095185,
                            "min_y": 72.63896221133226,
                        },
                        {
                            "max_x": 95.69535648357065,
                            "max_y": 57.09695671147431,
                            "min_x": 94.79616789633582,
                            "min_y": 56.580211738055716,
                        },
                        {
                            "max_x": 95.6350858150881,
                            "max_y": 6.344204438406445,
                            "min_x": 94.91730706851604,
                            "min_y": 6.329690351592068,
                        },
                        {
                            "max_x": 96.64692665810192,
                            "max_y": 27.32050171418362,
                            "min_x": 95.77372677147429,
                            "min_y": 26.74764015964408,
                        },
                        {
                            "max_x": 97.53135347858124,
                            "max_y": 58.83373184140501,
                            "min_x": 96.82819370943757,
                            "min_y": 57.89645331425522,
                        },
                        {
                            "max_x": 98.8983398159477,
                            "max_y": 30.39180129251106,
                            "min_x": 98.51205090529908,
                            "min_y": 29.432796087891944,
                        },
                    ],
                    "height": 1,
                    "is_leaf": True,
                },
            ],
            "height": 2,
            "is_leaf": False,
        },
    }

    assert tree.serialize() == expected
