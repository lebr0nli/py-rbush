#include "_rbush.h"
#include "debug.h"
#include <cmath>

namespace rbush {

// BBox implementation

double BBox::area() const { return (max_x - min_x) * (max_y - min_y); }

bool BBox::contains(const BBox &other) const {
    return min_x <= other.min_x && other.max_x <= max_x && min_y <= other.min_y &&
           other.max_y <= max_y;
}

double BBox::margin() const { return (max_x - min_x) + (max_y - min_y); }

double BBox::enlarged_area(const BBox &other) const {
    return (std::max(other.max_x, max_x) - std::min(other.min_x, min_x)) *
           (std::max(other.max_y, max_y) - std::min(other.min_y, min_y));
}

double BBox::intersection_area(const BBox &other) const {
    double min_max_x = std::max(min_x, other.min_x);
    double min_max_y = std::max(min_y, other.min_y);
    double max_min_x = std::min(max_x, other.max_x);
    double max_min_y = std::min(max_y, other.max_y);

    return std::max(0.0, max_min_x - min_max_x) * std::max(0.0, max_min_y - min_max_y);
}

bool BBox::intersects(const BBox &other) const {
    return other.min_x <= max_x && other.min_y <= max_y && other.max_x >= min_x &&
           other.max_y >= min_y;
}

void BBox::extend(const BBox &other) {
    min_x = std::min(min_x, other.min_x);
    min_y = std::min(min_y, other.min_y);
    max_x = std::max(max_x, other.max_x);
    max_y = std::max(max_y, other.max_y);
}

// Node implementation

template <typename T> BBox Node<T>::dist_bbox(int start, int end) const {
    BBox bbox;
    for (int i = start; i < end; ++i) {
        bbox.extend(*children[i]);
    }
    return bbox;
}

template <typename T> void Node<T>::calc_bbox() {
    BBox bbox;
    for (const auto &child : children) {
        bbox.extend(*child);
    }
    min_x = bbox.min_x;
    min_y = bbox.min_y;
    max_x = bbox.max_x;
    max_y = bbox.max_y;
}

// Explicit template instantiation for common types
template struct Node<py::dict>;
template struct Node<py::object>;

// RBushBase implementation

template <typename T>
RBushBase<T>::RBushBase(size_t max_entries)
    : _max_entries(std::max<size_t>(4, max_entries)),
      _min_entries(std::max<size_t>(2, std::ceil(_max_entries * 0.4))) {
    _root = std::make_unique<Node<T>>();
    _root->height = 1;
    _root->is_leaf = true;
}

template <typename T> void RBushBase<T>::clear() {
    _root = std::make_unique<Node<T>>();
    _root->height = 1;
    _root->is_leaf = true;
}

template <typename T> void RBushBase<T>::insert(const T &item) {
    DEBUG_TIMER("insert");
    std::unique_ptr<Node<T>> item_node = std::make_unique<Node<T>>(item);
    BBox bbox = to_bbox(item);
    item_node->min_x = bbox.min_x;
    item_node->min_y = bbox.min_y;
    item_node->max_x = bbox.max_x;
    item_node->max_y = bbox.max_y;
    _insert(std::move(item_node), _root->height - 1);
}

template <typename T> void RBushBase<T>::_insert(std::unique_ptr<Node<T>> item_node, int level) {
    std::vector<std::reference_wrapper<Node<T>>> insert_path;

    // find the best node for accommodating the item, saving all nodes along the path too
    Node<T> &insert_node = _choose_subtree(*item_node, *_root, level, insert_path);

    // Create a reference to the item_node before moving it
    const BBox &item_bbox = *item_node;

    // put the item into the node
    insert_node.children.push_back(std::move(item_node));
    insert_node.extend(item_bbox);

    // split on node overflow; propagate upwards if necessary
    while (level >= 0) {
        if (insert_path[level].get().children.size() > _max_entries) {
            _split(insert_path, level);
            --level;
        } else {
            break;
        }
    }

    // adjust bboxes along the insertion path
    _adjust_parent_bboxes(item_bbox, insert_path, level);
}

template <typename T>
Node<T> &RBushBase<T>::_choose_subtree(const BBox &bbox, Node<T> &node, int level,
                                       std::vector<std::reference_wrapper<Node<T>>> &path) {
    std::reference_wrapper<Node<T>> target_node = std::ref(node);
    while (true) {
        path.push_back(target_node);

        if (target_node.get().is_leaf || static_cast<int>(path.size()) - 1 == level)
            break;

        double min_area = std::numeric_limits<double>::infinity();
        double min_enlargement = std::numeric_limits<double>::infinity();
        bool found = false;

        for (const auto &child : target_node.get().children) {
            double area = child->area();
            double enlargement = child->enlarged_area(bbox) - area;

            if (enlargement < min_enlargement) {
                min_area = std::min(min_area, area);
                min_enlargement = enlargement;
                target_node = *child;
                found = true;
            } else if (enlargement == min_enlargement && area < min_area) {
                min_area = area;
                target_node = *child;
                found = true;
            }
        }
        if (!found)
            target_node = *target_node.get().children[0];
    }
    return target_node;
}

template <typename T>
void RBushBase<T>::_split(std::vector<std::reference_wrapper<Node<T>>> &insert_path, int level) {
    Node<T> &node = insert_path[level].get();
    const int M = node.children.size();
    const int m = _min_entries;

    _choose_split_axis(node, m, M);

    const int split_index = _choose_split_index(node, m, M);

    auto new_node = std::make_unique<Node<T>>();
    new_node->children.insert(new_node->children.end(),
                              std::make_move_iterator(node.children.begin() + split_index),
                              std::make_move_iterator(node.children.end()));
    node.children.resize(split_index);
    new_node->height = node.height;
    new_node->is_leaf = node.is_leaf;

    node.calc_bbox();
    new_node->calc_bbox();

    if (level) {
        insert_path[level - 1].get().children.push_back(std::move(new_node));
    } else {
        _split_root(node, *new_node);
    }
}

template <typename T>
void RBushBase<T>::_adjust_parent_bboxes(const BBox &bbox,
                                         std::vector<std::reference_wrapper<Node<T>>> &path,
                                         int level) {
    for (int i = level; i >= 0; --i) {
        path[i].get().extend(bbox);
    }
}

template <typename T> void RBushBase<T>::_split_root(Node<T> &node, Node<T> &new_node) {
    std::unique_ptr<Node<T>> new_root = std::make_unique<Node<T>>();
    new_root->height = node.height + 1;
    new_root->is_leaf = false;
    new_root->children.push_back(std::make_unique<Node<T>>(std::move(node)));
    new_root->children.push_back(std::make_unique<Node<T>>(std::move(new_node)));
    new_root->calc_bbox();
    _root = std::move(new_root);
}

template <typename T> int RBushBase<T>::_choose_split_index(Node<T> &node, int m, int M) {
    double min_overlap = std::numeric_limits<double>::infinity();
    double min_area = std::numeric_limits<double>::infinity();
    int split_index = M - m;

    for (int i = m; i <= M - m; ++i) {
        BBox bbox1 = node.dist_bbox(0, i);
        BBox bbox2 = node.dist_bbox(i, M);

        double overlap = bbox1.intersection_area(bbox2);
        double area = bbox1.area() + bbox2.area();

        if (overlap < min_overlap) {
            min_overlap = overlap;
            min_area = std::min(area, min_area);
            split_index = i;
        } else if (overlap == min_overlap && area < min_area) {
            min_area = area;
            split_index = i;
        }
    }

    return split_index;
}

template <typename T> void RBushBase<T>::_choose_split_axis(Node<T> &node, int m, int M) {
    double x_margin = _all_dist_margin(node, m, M, true);
    double y_margin = _all_dist_margin(node, m, M, false);

    if (x_margin < y_margin) {
        std::sort(node.children.begin(), node.children.end(),
                  [](const auto &a, const auto &b) { return a->min_x < b->min_x; });
    }
}

template <typename T>
double RBushBase<T>::_all_dist_margin(Node<T> &node, int m, int M, bool compare_min_x) {
    if (compare_min_x) {
        std::sort(node.children.begin(), node.children.end(),
                  [](const auto &a, const auto &b) { return a->min_x < b->min_x; });
    } else {
        std::sort(node.children.begin(), node.children.end(),
                  [](const auto &a, const auto &b) { return a->min_y < b->min_y; });
    }

    BBox left_bbox = node.dist_bbox(0, m);
    BBox right_bbox = node.dist_bbox(M - m, M);
    double margin = left_bbox.margin() + right_bbox.margin();

    for (int i = m; i < M - m; ++i) {
        left_bbox.extend(*node.children[i]);
        margin += left_bbox.margin();
    }

    for (int i = M - m - 1; i >= m; --i) {
        right_bbox.extend(*node.children[i]);
        margin += right_bbox.margin();
    }

    return margin;
}

template <typename T> void RBushBase<T>::load(std::vector<T> &items) {
    DEBUG_TIMER("load");
    if (items.empty())
        return;

    if (items.size() < _min_entries) {
        for (const auto &item : items) {
            insert(item);
        }
        return;
    }

    std::vector<std::unique_ptr<Node<T>>> nodes;
    nodes.reserve(items.size());
    for (auto &item : items) {
        auto node = std::make_unique<Node<T>>(item);
        BBox bbox = to_bbox(item);
        node->min_x = bbox.min_x;
        node->min_y = bbox.min_y;
        node->max_x = bbox.max_x;
        node->max_y = bbox.max_y;
        nodes.push_back(std::move(node));
    }

    // recursively build the tree with the given data from scratch using OMT algorithm
    auto node = _build(nodes, 0, nodes.size() - 1, 0);

    if (_root->children.empty()) {
        // save as is if tree is empty
        _root = std::move(node);
    } else if (_root->height == node->height) {
        // split root if trees have the same height
        _split_root(*_root, *node);
    } else {
        if (_root->height < node->height) {
            // swap trees if inserted one is bigger
            std::swap(_root, node);
        }

        // insert the small tree into the large tree at appropriate level
        int level = _root->height - node->height - 1;
        _insert(std::move(node), level);
    }
}

template <typename T>
std::unique_ptr<Node<T>> RBushBase<T>::_build(std::vector<std::unique_ptr<Node<T>>> &nodes,
                                              int left, int right, int height) {
    const int N = right - left + 1;
    int M = _max_entries;

    if (N <= M) {
        // reached leaf level; return leaf
        auto node = std::make_unique<Node<T>>();
        node->children.reserve(N);
        for (int i = left; i <= right; ++i) {
            node->children.push_back(std::move(nodes[i]));
        }
        node->calc_bbox();
        return node;
    }

    if (!height) {
        // target height of the bulk-loaded tree
        height = std::ceil(std::log(N) / std::log(M));

        // target number of root entries to maximize storage utilization
        M = std::ceil(N / std::pow(M, height - 1));
    }

    auto node = std::make_unique<Node<T>>();
    node->is_leaf = false;
    node->height = height;

    // split the items into M mostly square tiles
    const int N2 = std::ceil(static_cast<double>(N) / M);
    const int N1 = N2 * std::ceil(std::sqrt(M));

    _multi_select(nodes, left, right, N1, true);

    for (int i = left; i <= right; i += N1) {
        const int right2 = std::min(i + N1 - 1, right);
        _multi_select(nodes, i, right2, N2, false);

        for (int j = i; j <= right2; j += N2) {
            const int right3 = std::min(j + N2 - 1, right2);
            // pack each entry recursively
            node->children.push_back(_build(nodes, j, right3, height - 1));
        }
    }

    node->calc_bbox();
    return node;
}

template <typename T>
void RBushBase<T>::_multi_select(std::vector<std::unique_ptr<Node<T>>> &nodes, int left, int right,
                                 int n, bool compare_min_x) {
    std::vector<int> stack = {left, right};

    while (!stack.empty()) {
        right = stack.back();
        stack.pop_back();
        left = stack.back();
        stack.pop_back();

        if (right - left <= n)
            continue;

        const int mid = left + std::ceil(static_cast<double>(right - left) / n / 2) * n;
        _quick_select(nodes, mid, left, right, compare_min_x);

        stack.push_back(left);
        stack.push_back(mid);
        stack.push_back(mid);
        stack.push_back(right);
    }
}

template <typename T>
void RBushBase<T>::_quick_select(std::vector<std::unique_ptr<Node<T>>> &arr, int k, int left,
                                 int right, bool compare_min_x) const {
    while (right > left) {
        if (right - left > 600) {
            const double n = right - left + 1;
            const double m = k - left + 1;
            const double z = std::log(n);
            const double s = 0.5 * std::exp(2 * z / 3);
            const double sd = 0.5 * std::sqrt(z * s * (n - s) / n) * (m - n / 2 < 0 ? -1 : 1);
            const int new_left = std::max(left, static_cast<int>(std::floor(k - m * s / n + sd)));
            const int new_right =
                std::min(right, static_cast<int>(std::floor(k + (n - m) * s / n + sd)));
            _quick_select(arr, k, new_left, new_right, compare_min_x);
        }

        const std::reference_wrapper<Node<T>> t = *arr[k];
        int i = left;
        int j = right;

        std::swap(arr[left], arr[k]);
        if (_compare_node_min(*arr[right], t, compare_min_x) > 0) {
            std::swap(arr[left], arr[right]);
        }

        while (i < j) {
            std::swap(arr[i], arr[j]);
            ++i;
            --j;
            while (_compare_node_min(*arr[i], t, compare_min_x) < 0)
                ++i;
            while (_compare_node_min(*arr[j], t, compare_min_x) > 0) {
                --j;
            }
        }

        if (_compare_node_min(*arr[left], t, compare_min_x) == 0) {
            std::swap(arr[left], arr[j]);
        } else {
            ++j;
            std::swap(arr[j], arr[right]);
        }

        if (j <= k)
            left = j + 1;
        if (k <= j)
            right = j - 1;
    }
}

template <typename T>
double RBushBase<T>::_compare_node_min(const BBox &a, const BBox &b, bool compare_min_x) const {
    return compare_min_x ? a.min_x - b.min_x : a.min_y - b.min_y;
}

template <typename T>
void RBushBase<T>::remove(const T &item, const std::function<bool(const T &, const T &)> &equals) {
    DEBUG_TIMER("remove");
    BBox bbox = to_bbox(item);
    std::vector<std::reference_wrapper<Node<T>>> path;
    std::vector<size_t> children_indexes;
    std::reference_wrapper<Node<T>> current_node = std::ref(*_root);
    size_t children_index = 0;
    bool going_up = false;

    // depth-first iterative tree traversal
    while (true) {
        if (current_node.get().is_leaf) { // search for item
            auto it = std::find_if(
                current_node.get().children.begin(), current_node.get().children.end(),
                [&](const std::unique_ptr<Node<T>> &child) {
                    return equals ? equals(*child->data, item) : (*child->data).is(item);
                });
            if (it != current_node.get().children.end()) {
                current_node.get().children.erase(it);
                path.push_back(current_node);
                _condense(path);
                return;
            }
        }

        if (!going_up && !current_node.get().is_leaf &&
            current_node.get().contains(bbox)) { // go down
            path.push_back(current_node);
            children_indexes.push_back(children_index);
            children_index = 0;
            current_node = *current_node.get().children[0];
        } else if (!path.empty() &&
                   children_index + 1 < path.back().get().children.size()) { // go right
            going_up = false; // can go down when visiting a new node
            current_node = *path.back().get().children[++children_index];
        } else if (!path.empty()) { // go up
            current_node = path.back();
            children_index = children_indexes.back();
            path.pop_back();
            children_indexes.pop_back();
            going_up = true; // so it won't go down again when we back to parent
        } else {
            // if we can't go down, up or right, then we're done
            return;
        }
    }
}

template <typename T>
void RBushBase<T>::_condense(std::vector<std::reference_wrapper<Node<T>>> &path) {
    for (int i = path.size() - 1; i >= 0; --i) {
        Node<T> &node = path[i].get();
        if (node.children.empty()) {
            if (i > 0) {
                Node<T> &parent = path[i - 1].get();
                auto it = std::find_if(
                    parent.children.begin(), parent.children.end(),
                    [&](const std::unique_ptr<Node<T>> &child) { return child.get() == &node; });
                if (it != parent.children.end()) {
                    parent.children.erase(it);
                }
            } else {
                clear();
            }
        } else {
            node.calc_bbox();
        }
    }
}

template <typename T>
std::vector<std::reference_wrapper<T>> RBushBase<T>::search(const BBox &bbox) const {
    DEBUG_TIMER("search");
    std::vector<std::reference_wrapper<T>> result;
    if (!bbox.intersects(*_root))
        return result;

    std::vector<std::reference_wrapper<const Node<T>>> nodes_to_search;
    nodes_to_search.push_back(std::cref(*_root));
    while (!nodes_to_search.empty()) {
        const Node<T> &node = nodes_to_search.back().get();
        nodes_to_search.pop_back();
        for (const auto &child : node.children) {
            if (bbox.intersects(*child)) {
                if (node.is_leaf) {
                    result.push_back(*child->data);
                } else if (bbox.contains(*child)) {
                    _all(*child, result);
                } else {
                    nodes_to_search.push_back(std::cref(*child));
                }
            }
        }
    }
    return result;
}

template <typename T> bool RBushBase<T>::collides(const BBox &bbox) const {
    DEBUG_TIMER("collides");
    std::vector<std::reference_wrapper<const Node<T>>> nodes_to_search;
    nodes_to_search.push_back(std::cref(*_root));
    while (!nodes_to_search.empty()) {
        const Node<T> &node = nodes_to_search.back().get();
        nodes_to_search.pop_back();
        for (const auto &child : node.children) {
            if (bbox.intersects(*child)) {
                if (node.is_leaf || bbox.contains(*child)) {
                    return true;
                } else {
                    nodes_to_search.push_back(std::cref(*child));
                }
            }
        }
    }
    return false;
}

template <typename T> std::vector<std::reference_wrapper<T>> RBushBase<T>::all() const {
    DEBUG_TIMER("all");
    std::vector<std::reference_wrapper<T>> result;
    _all(*_root, result);
    return result;
}

template <typename T>
void RBushBase<T>::_all(std::reference_wrapper<Node<T>> start_node,
                        std::vector<std::reference_wrapper<T>> &result) const {
    std::vector<std::reference_wrapper<const Node<T>>> nodes_to_search;
    nodes_to_search.push_back(start_node);
    while (!nodes_to_search.empty()) {
        const Node<T> &node = nodes_to_search.back().get();
        nodes_to_search.pop_back();
        if (node.is_leaf) {
            for (const auto &child : node.children) {
                result.push_back(*child->data);
            }
        } else {
            for (const auto &child : node.children) {
                nodes_to_search.push_back(std::cref(*child));
            }
        }
    }
}

template <typename T> py::dict RBushBase<T>::serialize() const {
    DEBUG_TIMER("serialize");
    py::dict result;
    result["max_entries"] = _max_entries;
    result["min_entries"] = _min_entries;
    result["root"] = _serialize_node(*_root);
    return result;
}

template <typename T> py::dict RBushBase<T>::_serialize_node(const Node<T> &node) const {
    py::dict data;
    data["bbox"] = py::dict(py::arg("min_x") = node.min_x, py::arg("min_y") = node.min_y,
                            py::arg("max_x") = node.max_x, py::arg("max_y") = node.max_y);
    data["height"] = node.height;
    data["is_leaf"] = node.is_leaf;

    py::list children;
    for (const auto &child : node.children) {
        if (node.is_leaf) {
            children.append(*child->data);
        } else {
            children.append(_serialize_node(*child));
        }
    }
    data["children"] = children;
    return data;
}

template <typename T> void RBushBase<T>::deserialize(const py::dict &data) {
    DEBUG_TIMER("deserialize");
    _max_entries = data["max_entries"].cast<size_t>();
    _min_entries = data["min_entries"].cast<size_t>();
    _root = _deserialize_node(data["root"]);
}

template <typename T>
std::unique_ptr<Node<T>> RBushBase<T>::_deserialize_node(const py::dict &data) {
    auto node = std::make_unique<Node<T>>();

    py::dict bbox = data["bbox"];
    node->min_x = bbox["min_x"].cast<double>();
    node->min_y = bbox["min_y"].cast<double>();
    node->max_x = bbox["max_x"].cast<double>();
    node->max_y = bbox["max_y"].cast<double>();

    node->height = data["height"].cast<int>();
    node->is_leaf = data["is_leaf"].cast<bool>();

    py::list children = data["children"];
    for (const auto &child : children) {
        if (node->is_leaf) {
            auto leaf_node = std::make_unique<Node<T>>(child.cast<T>());
            BBox bbox = to_bbox(child.cast<T>());
            leaf_node->min_x = bbox.min_x;
            leaf_node->min_y = bbox.min_y;
            leaf_node->max_x = bbox.max_x;
            leaf_node->max_y = bbox.max_y;
            node->children.push_back(std::move(leaf_node));
        } else {
            node->children.push_back(_deserialize_node(child.cast<py::dict>()));
        }
    }
    return node;
}

// RBush implementation

BBox RBush::to_bbox(const py::dict &item) const {
    double min_x = item["min_x"].cast<double>();
    double min_y = item["min_y"].cast<double>();
    double max_x = item["max_x"].cast<double>();
    double max_y = item["max_y"].cast<double>();
    return BBox(min_x, min_y, max_x, max_y);
}

// Explicit template instantiation
template class RBushBase<py::dict>;
template class RBushBase<py::object>;

} // namespace rbush
