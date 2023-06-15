import pkg1
import pytest
from pkg1.mod1 import class_inst1

from dynamic_imports import search
from tests.pkg1.mod1 import Base
from tests.pkg1.pkg2 import mod2


@pytest.mark.parametrize(
    "search_subpackages,result",
    [(True, ["pkg1.mod1", "pkg1.pkg2.mod2"]), (False, ["pkg1.mod1"])],
)
def test_module_search(search_subpackages, result):
    module_names = [
        m.__name__
        for m in search.discover_modules(pkg1, search_subpackages=search_subpackages)
    ]
    assert module_names == result


@pytest.mark.parametrize("base_class", [Base, "Base"])
@pytest.mark.parametrize("module", [mod2, "tests.pkg1.pkg2.mod2"])
def test_module_class_impl(base_class, module):
    class_impl = search.class_impls(
        base_class=base_class, search_in=module, names_only=True
    )
    assert class_impl == ["ClassImpl2"]


@pytest.mark.parametrize("base_class", [Base, "Base"])
@pytest.mark.parametrize("package", [pkg1, "pkg1"])
@pytest.mark.parametrize(
    "search_subpackages,result",
    [(True, ["ClassImpl1", "ClassImpl2"]), (False, ["ClassImpl1"])],
)
def test_pkg_class_impl(base_class, package, search_subpackages, result):
    class_impl = search.class_impls(
        base_class=base_class,
        search_in=package,
        search_subpackages=search_subpackages,
        names_only=True,
    )
    assert class_impl == result


@pytest.mark.parametrize("module", [mod2, "tests.pkg1.pkg2.mod2"])
def test_module_class_inst(module):
    class_inst = search.class_inst(mod2.ClassImpl2, module)
    assert class_inst == [mod2.class_inst2]


@pytest.mark.parametrize("package", [pkg1, "pkg1"])
@pytest.mark.parametrize("search_subpackages", [True, False])
def test_pkg_class_inst(package, search_subpackages):
    class_inst = search.class_inst(
        class_type=pkg1.mod1.ClassImpl1,
        search_in=package,
        search_subpackages=search_subpackages,
    )
    assert class_inst == [class_inst1]
