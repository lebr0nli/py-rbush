#include "_rbush.h"
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

void BBox::extend(const BBox &other) {
    min_x = std::min(min_x, other.min_x);
    min_y = std::min(min_y, other.min_y);
    max_x = std::max(max_x, other.max_x);
    max_y = std::max(max_y, other.max_y);
}

// Node implementation

template <typename T> BBox Node<T>::dist_bbox(int start, int end) const {
    BBox bbox;
    for (int i = start; i < end; i++) {
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
    : _max_entries(max_entries), _min_entries(std::max<size_t>(2, max_entries / 2)) {
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

        double min_area = std::numeric_limits<double>::max();
        double min_enlargement = std::numeric_limits<double>::max();
        bool found = false;

        for (const auto &child : target_node.get().children) {
            double area = child->area();
            double enlargement = child->enlarged_area(bbox) - area;

            if (enlargement < min_enlargement ||
                (enlargement == min_enlargement && area < min_area)) {
                target_node = *child;
                found = true;
            }

            min_area = std::min(min_area, area);
            min_enlargement = std::min(min_enlargement, enlargement);
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
    double min_overlap = std::numeric_limits<double>::max();
    double min_area = std::numeric_limits<double>::max();
    int split_index = m;

    for (int i = m; i <= M - m; i++) {
        BBox bbox1 = node.dist_bbox(0, i);
        BBox bbox2 = node.dist_bbox(i, M);

        double overlap = bbox1.intersection_area(bbox2);
        double area = bbox1.area() + bbox2.area();

        if (overlap < min_overlap || (overlap == min_overlap && area < min_area)) {
            min_overlap = overlap;
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
                  [](const auto &a, const auto &b) { return BBox::compare_min_x(*a, *b); });
    }
}

template <typename T>
double RBushBase<T>::_all_dist_margin(Node<T> &node, int m, int M, bool compare_min_x) {
    if (compare_min_x) {
        std::sort(node.children.begin(), node.children.end(),
                  [](const auto &a, const auto &b) { return BBox::compare_min_x(*a, *b); });
    } else {
        std::sort(node.children.begin(), node.children.end(),
                  [](const auto &a, const auto &b) { return BBox::compare_min_y(*a, *b); });
    }

    double margin_sum = 0;
    for (int i = 0; i < M - m + 1; i++) {
        BBox bbox1 = node.dist_bbox(0, m + i);
        BBox bbox2 = node.dist_bbox(m + i, M);
        margin_sum += bbox1.margin() + bbox2.margin();
    }

    return margin_sum;
}

template <typename T>
void RBushBase<T>::remove(const T &item, const std::function<bool(const T &, const T &)> &equals) {
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

template <typename T> std::vector<std::reference_wrapper<T>> RBushBase<T>::all() const {
    std::vector<std::reference_wrapper<T>> result;
    std::vector<std::reference_wrapper<const Node<T>>> nodes_to_search;
    nodes_to_search.push_back(std::cref(*_root));
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
    return result;
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
