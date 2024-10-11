#include "_rbush.h"

#include <algorithm>
#include <cmath>

RBush::RBush(int max_entries) {
    _max_entries = std::max(4, max_entries);
    _min_entries = std::max(2, (int)std::ceil(_max_entries * 0.4));
}