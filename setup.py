from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in alhamdent/__init__.py
from alhamdent import __version__ as version

setup(
	name="alhamdent",
	version=version,
	description="Al Hamd Enterprises",
	author="VUT",
	author_email="safdar211@gmail.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
