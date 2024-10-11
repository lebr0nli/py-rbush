#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "_rbush.h"

PYBIND11_MODULE(_rbush, m) {
    m.doc() = "Internal module for py-rbush";

    pybind11::class_<RBush>(m, "RBush")
        .def(pybind11::init<int>(), pybind11::arg("max_entries") = 9);
}