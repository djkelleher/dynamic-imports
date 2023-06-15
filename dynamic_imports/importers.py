import importlib
import importlib.util
from functools import lru_cache
from pathlib import Path
from types import ModuleType
from typing import Any, Union


@lru_cache
def import_module(name_or_path: Union[Path, str]) -> ModuleType:
    """Import a module.

    Args:
        name_or_path (Union[Path, str]): Name of module (e.g. `my_package.my_module`) or path to module file (e.g. `/home/user/my_package/my_module.py`)

    Returns:
        ModuleType: The imported module.
    """
    if (path := Path(name_or_path)).suffix == ".py":
        # import module from file path.
        module_spec = importlib.util.spec_from_file_location(
            path.stem, str(name_or_path)
        )
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        return module
    # import installed module.
    return importlib.import_module(str(name_or_path))


def import_module_attr(module_name_or_path: Union[Path, str], attr_name: str) -> Any:
    """Get reference to a module's attribute (e.g. a function or class), importing the module if needed.

    Args:
        module_name_or_path (Union[Path, str]): Name of module (e.g. `requests`) or path to module file (e.g. `/home/user/my_package/my_module.py`)
        attr_name (str): Name of the attribute.

    Returns:
        Any: The attribute.
    """
    module = import_module(module_name_or_path)
    if not hasattr(module, attr_name):
        raise AttributeError(
            f"Could not load {attr_name} from module {module_name_or_path}!"
        )
    return getattr(module, attr_name)
