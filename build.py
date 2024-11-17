from pybind11.setup_helpers import Pybind11Extension


def build(setup_kwargs: dict):
    ext_modules = [
        Pybind11Extension(
            "_rbush",
            sources=["_rbush/module.cc", "_rbush/_rbush.cc"],
            depends=["_rbush/_rbush.h"],
            extra_compile_args=["-O3", "-Wall", "-Wextra", "-Werror"],
            language="c++",
            cxx_std=17,
        ),
    ]
    setup_kwargs.update(
        {
            "ext_modules": ext_modules,
            "zip_safe": False,
        }
    )
