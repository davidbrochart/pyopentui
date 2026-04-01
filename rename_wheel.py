import sys

from packaging.tags import sys_tags
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


tags = list(sys_tags())

# The first tag is the most specific for the system
best_tag = str(tags[0])

pyproject = tomllib.loads(Path("pyproject.toml").read_text())
package_name = pyproject["project"]["name"]
version = pyproject["project"]["version"]
python_tag, abi_tag, platform_tag = best_tag.split("-")
wheel_name = f"{package_name}-{version}-{python_tag}-{abi_tag}-{platform_tag}.whl"
(Path("dist") / f"pyopentui-{version}-py3-none-any.whl").rename(Path("dist") / wheel_name)
