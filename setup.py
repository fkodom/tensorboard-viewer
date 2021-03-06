import os
from distutils.core import setup
from subprocess import getoutput

import setuptools


def get_version_tag() -> str:
    try:
        env_key = "TENSORBOARD_VIEWER_VERSION".upper()
        version = os.environ[env_key]
    except KeyError:
        version = getoutput("git describe --tags --abbrev=0")

    if version.lower().startswith("fatal"):
        version = "0.0.0"

    return version


extras_require = {
    "test": ["black", "flake8", "isort", "mypy", "pytest", "pytest-cov"],
}
extras_require["dev"] = ["pre-commit", *extras_require["test"]]
all_require = [r for reqs in extras_require.values() for r in reqs]
extras_require["all"] = all_require


setup(
    name="tensorboard-viewer",
    version=get_version_tag(),
    author="Frank Odom",
    author_email="frank.odom.iii@gmail.com",
    url="https://github.com/fkodom/tensorboard-viewer",
    packages=setuptools.find_packages(exclude=["tests"]),
    description="Minimal project for aggregating and viewing remote and local Tensorboard logs.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    install_requires=["fsspec", "tqdm", "tensorboard"],
    extras_require=extras_require,
    entry_points={
        "console_scripts": ["tensorboard-viewer=tensorboard_viewer.main:main"]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
