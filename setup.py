import os

from setuptools import find_packages, setup
from importlib.util import spec_from_file_location, module_from_spec


def read(file_name):
    with open(os.path.join(os.path.dirname(__file__), file_name)) as file:
        return file.read()


def get_version():
    version_file = os.path.join(os.path.dirname(__file__), "appearance", "__version__.py")
    try:
        spec = spec_from_file_location("__version__", version_file)
        version_module = module_from_spec(spec)
        spec.loader.exec_module(version_module)
        return version_module.__version__
    except (FileNotFoundError, AttributeError) as e:
        raise RuntimeError(f"Unable to find version in {version_file}") from e


setup(
    name="mb-app",
    version=get_version(),
    author="doppelmarker",
    author_email="doppelmarker@gmail.com",
    url="https://github.com/doppelmarker/mb_appearance",
    description="Python util for Mount&Blade characters file manipulation.",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    python_requires=">=3.8",
    classifiers=["Programming Language :: Python :: 3.8"],
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=read("requirements.txt").splitlines(),
    entry_points={
        "console_scripts": [
            "mb-app=appearance.app:main",
        ],
    },
)
