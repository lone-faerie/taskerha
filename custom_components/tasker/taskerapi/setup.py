"""Setup module for taskerapi"""
from pathlib import Path
from setuptools import setup

PROJECT_DIR = Path(__file__).parent.resolve()
README_FILE = PROJECT_DIR / "README.md"
VERSION = "0.3.3"
INSTALL_REQUIREMENTS = ["aiohttp", "async_timeout", "orjson", "xmltodict"]

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="taskerapi",
    version=VERSION,
    url="https://github.com/lone-faerie/taskerapi",
    download_url="https://github.com/lone-faerie/taskerapi",
    author="Lone Faerie",
    author_email="lone.faerie@gmail.com",
    description="Library to control Tasker Android app",
    long_description=README_FILE.read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    license="GPLv3",
    packages=["taskerapi"],
    python_requires=">=3.9",
    install_requirements=INSTALL_REQUIREMENTS,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    package_data={"taskerapi.data": ["*.xml"]}
)