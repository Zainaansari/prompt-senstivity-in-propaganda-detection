import os
from setuptools import setup
 
SRC_DIR = "src"
py_modules = [
    os.path.splitext(f)[0]
    for f in os.listdir(SRC_DIR)
    if f.endswith(".py") and f != "__init__.py"
]
 
setup(
    package_dir={"": SRC_DIR},
    py_modules=py_modules,
)