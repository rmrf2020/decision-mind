import pkgutil
import importlib
import os

# 动态发现当前包中的模块
MODULES = {}

# 获取当前包的名称
package_name = os.path.basename(os.path.dirname(__file__))

# 动态扫描包中的模块
for _, module_name, _ in pkgutil.iter_modules([os.path.dirname(__file__)]):
    full_module_name = f"{package_name}.{module_name}"
    module = importlib.import_module(full_module_name)
    if hasattr(module, "info"):
        info = module.info()
        MODULES[info.name] = [full_module_name, info]


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
