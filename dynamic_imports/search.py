import pkgutil
import pyclbr
from pathlib import Path
from types import ModuleType
from typing import List, Union

from .importers import import_module


def discover_modules(
    package: Union[ModuleType, str],
    search_subpackages: bool = True,
    names_only: bool = False,
) -> Union[List[str], List[ModuleType]]:
    """Find all modules in a package or nested packages.

    Args:
        package (Union[ModuleType, str]): Top-level package where search should begin.
        search_subpackages (bool, optional): Search sub-packages within `package`. Defaults to True.
        names_only (bool, optional): Return module names.

    Returns:
        Union[List[str], List[ModuleType]]: The discovered modules or module names.
    """
    if isinstance(package, str):
        # import the package.
        package = import_module(package)
    if package.__package__ != package.__name__:
        # `package` is a module, not a package.
        return [package] if not names_only else [package.__name__]
    # search for module names.
    searcher = pkgutil.walk_packages if search_subpackages else pkgutil.iter_modules
    module_names = [
        name
        for _, name, ispkg in searcher(package.__path__, f"{package.__name__}.")
        if not ispkg
    ]
    if names_only:
        return module_names
    # import the discovered modules.
    return [import_module(name) for name in module_names]


def class_impls(
    base_class: Union[ModuleType, str],
    search_in: Union[ModuleType, str],
    search_subpackages: bool = True,
    names_only: bool = False,
) -> Union[List[str], List[ModuleType]]:
    """Find all implementations of a base class within a module or package.

    Args:
        base_class (Union[ModuleType, str]): The base class who's implementations should be searched for.
        search_in (Union[ModuleType, str]): The module or package to search in.
        search_subpackages (bool, optional): Search sub-packages within `package`. Defaults to True.
        names_only (bool, optional): Return class names. Defaults to False.

    Returns:
        Union[List[str], List[ModuleType]]: The discovered classes or class names.
    """
    _class_impls = []
    for module in discover_modules(search_in, search_subpackages, names_only):
        if isinstance(module, str):
            if names_only:
                # check if module_name is a path to a Python file.
                if (module_path := Path(module)).is_file():
                    # read python file path
                    module_classes = pyclbr.readmodule(
                        module_path.stem, path=module_path.parent
                    )
                else:
                    # read installed module path.
                    module_classes = pyclbr.readmodule(module)
                base_class = (
                    base_class if isinstance(base_class, str) else base_class.__name__
                )
                _class_impls += [
                    cls_name
                    for cls_name, cls_obj in module_classes.items()
                    if any(getattr(s, "name", s) == base_class for s in cls_obj.super)
                ]
                continue
            module = import_module(module)
        # parse the imported module.
        if isinstance(base_class, str):
            _class_impl_objs = [
                o
                for o in module.__dict__.values()
                if base_class in [c.__name__ for c in getattr(o, "__bases__", [])]
            ]
        else:
            _class_impl_objs = [
                o
                for o in module.__dict__.values()
                if base_class in getattr(o, "__bases__", [])
            ]

        _class_impls += (
            [c.__name__ for c in _class_impl_objs] if names_only else _class_impl_objs
        )
    return _class_impls


def class_inst(
    class_type: ModuleType,
    search_in: Union[ModuleType, str],
    search_subpackages: bool = True,
) -> List[ModuleType]:
    """Find all instances of a class within a package or module.

    Args:
        class_type (ModuleType): The class who's instances should be searched for.
        search_in (Union[ModuleType, str]): The package or module to search in.
        search_subpackages (bool, optional): Search sub-packages within `package`. Defaults to True.

    Returns:
        List[ModuleType]: The discovered class instances.
    """
    if isinstance(search_in, (Path, str)):
        search_in = import_module(search_in)
    instances = [
        c
        for module in discover_modules(search_in, search_subpackages)
        for c in module.__dict__.values()
        if isinstance(c, class_type)
    ]
    return list({id(i): i for i in instances}.values())
