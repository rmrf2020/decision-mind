import pkgutil
import importlib
import os

MODULES = {}


def scan_package(package_path, package_name):
    """
    """
    for _, module_name, is_pkg in pkgutil.iter_modules([package_path]):
        full_module_name = f"{package_name}.{module_name}"
        module = importlib.import_module(full_module_name)
        if hasattr(module, "info"):
            info = module.info()
            MODULES[info.name] = [full_module_name, info]

        if is_pkg:
            sub_package_path = os.path.join(package_path, module_name)
            sub_package_name = f"{package_name}.{module_name}"
            scan_package(sub_package_path, sub_package_name)


async def router(name, method="handler", arguments: dict = None):
    if name not in MODULES:
        raise ValueError(f"Module {name} not found")
    module = importlib.import_module(MODULES[name][0])
    if not hasattr(module, method):
        raise AttributeError(f"Module {name} does not have method {method}")
    target_method = getattr(module, method)
    if arguments is not None and isinstance(arguments, dict):
        return await target_method(**arguments)
    else:
        return await target_method()


current_package_name = os.path.basename(os.path.dirname(__file__))
scan_package(os.path.dirname(__file__), current_package_name)
