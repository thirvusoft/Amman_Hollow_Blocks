from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in hollow_blocks/__init__.py
from hollow_blocks import __version__ as version

setup(
	name="hollow_blocks",
	version=version,
	description="Hollow Blllllllocks",
	author="TS",
	author_email="ts@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
