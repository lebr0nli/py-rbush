#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "_rbush.h"

namespace py = pybind11;

PYBIND11_MODULE(_rbush, m) {
    m.doc() = "Internal module for py-rbush";

    py::class_<rbush::BBox>(m, "BBox")
        .def(py::init<>())
        .def(py::init<double, double, double, double>())
        .def_readwrite("min_x", &rbush::BBox::min_x)
        .def_readwrite("min_y", &rbush::BBox::min_y)
        .def_readwrite("max_x", &rbush::BBox::max_x)
        .def_readwrite("max_y", &rbush::BBox::max_y)
        .def("area", &rbush::BBox::area)
        .def("margin", &rbush::BBox::margin)
        .def("enlarged_area", &rbush::BBox::enlarged_area)
        .def("intersection_area", &rbush::BBox::intersection_area)
        .def("extend", &rbush::BBox::extend);

    py::class_<rbush::RBushBase<py::object>, rbush::PyRBushBase>(m, "RBushBase")
        .def(py::init<int>(), py::arg("max_entries") = 9)
        .def("clear", &rbush::RBushBase<py::object>::clear)
        .def("insert", &rbush::RBushBase<py::object>::insert, py::arg("item"))
        .def("all", &rbush::RBushBase<py::object>::all)
        .def("to_bbox", &rbush::RBushBase<py::object>::to_bbox, py::arg("item"));

    py::class_<rbush::RBush>(m, "RBush")
        .def(py::init<int>(), py::arg("max_entries") = 9)
        .def("clear", &rbush::RBushBase<py::dict>::clear)
        .def("insert", &rbush::RBushBase<py::dict>::insert, py::arg("item"))
        .def("all", &rbush::RBushBase<py::dict>::all)
        .def("to_bbox", &rbush::RBush::to_bbox, py::arg("item"));
}
