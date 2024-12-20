#ifndef _RBUSH_H_
#define _RBUSH_H_

#include <algorithm>
#include <limits>
#include <memory>
#include <pybind11/pybind11.h>
#include <vector>

namespace py = pybind11;

namespace rbush {

// Bounding box structure
struct BBox {
    double min_x;
    double min_y;
    double max_x;
    double max_y;

    BBox()
        : min_x(std::numeric_limits<double>::infinity()),
          min_y(std::numeric_limits<double>::infinity()),
          max_x(-std::numeric_limits<double>::infinity()),
          max_y(-std::numeric_limits<double>::infinity()) {}

    BBox(double min_x, double min_y, double max_x, double max_y)
        : min_x(min_x), min_y(min_y), max_x(max_x), max_y(max_y) {}

    double area() const;
    bool contains(const BBox &other) const;
    double margin() const;
    double enlarged_area(const BBox &other) const;
    double intersection_area(const BBox &other) const;
    bool intersects(const BBox &other) const;
    void extend(const BBox &other);
};

// Node structure for R-tree
template <typename T> struct Node : public BBox {
    std::vector<std::unique_ptr<Node<T>>> children;
    std::unique_ptr<T> data;
    int height;
    bool is_leaf;

    Node() : BBox(), height(1), is_leaf(true) {}
    Node(const T &item) : BBox(), data(std::make_unique<T>(item)), height(1), is_leaf(true) {}
    Node(T &&item) : BBox(), data(std::make_unique<T>(std::move(item))), height(1), is_leaf(true) {}

    BBox dist_bbox(int start, int end) const;
    void calc_bbox();
};

// Base class for RBush
template <typename T> class RBushBase {
public:
    explicit RBushBase(size_t max_entries = 9);
    virtual ~RBushBase() = default;

    RBushBase(const RBushBase &) = delete;
    RBushBase &operator=(const RBushBase &) = delete;
    RBushBase(RBushBase &&) = default;
    RBushBase &operator=(RBushBase &&) = default;

    void clear();
    void insert(const T &item);
    void load(std::vector<T> &items);
    void remove(const T &item, const std::function<bool(const T &, const T &)> &equals = nullptr);
    std::vector<std::reference_wrapper<T>> search(const BBox &bbox) const;
    bool collides(const BBox &bbox) const;
    std::vector<std::reference_wrapper<T>> all() const;
    py::dict serialize() const;
    void deserialize(const py::dict &data);

    virtual BBox to_bbox(const T &item) const = 0;

private:
    size_t _max_entries;
    size_t _min_entries;
    std::unique_ptr<Node<T>> _root;

    void _insert(std::unique_ptr<Node<T>> item_node, int level);
    Node<T> &_choose_subtree(const BBox &bbox, Node<T> &node, int level,
                             std::vector<std::reference_wrapper<Node<T>>> &path);
    void _split(std::vector<std::reference_wrapper<Node<T>>> &insert_path, int level);
    void _adjust_parent_bboxes(const BBox &bbox, std::vector<std::reference_wrapper<Node<T>>> &path,
                               int level);
    void _split_root(Node<T> &node, Node<T> &new_node);
    int _choose_split_index(Node<T> &node, int m, int M);
    void _choose_split_axis(Node<T> &node, int m, int M);
    double _all_dist_margin(Node<T> &node, int m, int M, bool compare_min_x);
    void _condense(std::vector<std::reference_wrapper<Node<T>>> &path);
    void _all(std::reference_wrapper<Node<T>>,
              std::vector<std::reference_wrapper<T>> &result) const;
    std::unique_ptr<Node<T>> _build(std::vector<std::unique_ptr<Node<T>>> &nodes, int left,
                                    int right, int height);
    void _multi_select(std::vector<std::unique_ptr<Node<T>>> &nodes, int left, int right, int n,
                       bool compare_min_x);
    void _quick_select(std::vector<std::unique_ptr<Node<T>>> &nodes, int k, int left, int right,
                       bool compare_min_x) const;
    double _compare_node_min(const BBox &a, const BBox &b, bool compare_min_x) const;
    py::dict _serialize_node(const Node<T> &node) const;
    std::unique_ptr<Node<T>> _deserialize_node(const py::dict &data);
};

// Default implementation that takes a Python dictionary as input
class RBush : public RBushBase<py::dict> {
public:
    using RBushBase<py::dict>::RBushBase;

    BBox to_bbox(const py::dict &item) const override;
};

// Python helper class for subclassing
class PyRBushBase : public RBushBase<py::object> {
public:
    using RBushBase<py::object>::RBushBase;

    typedef RBushBase<py::object> BaseT;

    BBox to_bbox(const py::object &item) const override {
        PYBIND11_OVERRIDE_PURE(BBox, BaseT, to_bbox, item);
    }
};

} // namespace rbush

#endif // _RBUSH_H_
