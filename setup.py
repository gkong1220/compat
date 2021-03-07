import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name="compat",
    version="0.1",
    entry_points={
        "console_scripts": ["compat=compat:main"]
    },
    description="check requirements.txt for compatability with specific python version",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/gkong1220/compat.git",
    author="Gabriel Kong",
    author_email="gabrielmkong@gmail.com",
    license="MIT",
    packages=["compat"],
    zip_safe=True
)