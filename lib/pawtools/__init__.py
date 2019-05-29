
# PAW Utilities
from .parser import *
from .logger import *
from .timestamp import *

# PAW Runtime
from .workload import *
from .verify import *
from .analyze import *

from .plots import *

_import = __import__("importlib")

runtimes = dict()
for _mod_name in {"workload.execute", "verify", "analyze"}:
    _mod = _import.import_module(".%s" % _mod_name, "pawtools")
    if hasattr(_mod, "__runtime__"):
        for _rt_name in getattr(_mod, "__runtime__"):
            runtimes.update(
                {_rt_name: getattr(_mod, _rt_name)}
            )


