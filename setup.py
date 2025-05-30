import os

from setuptools import find_packages, setup


def read(file_name):
    with open(os.path.join(os.path.dirname(__file__), file_name)) as file:
        return file.read()


def get_version():
    version_file = os.path.join(os.path.dirname(__file__), "appearance", "__version__.py")
    with open(version_file) as f:
        exec(compile(f.read(), version_file, "exec"))
    return locals()["__version__"]


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
