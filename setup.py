from setuptools import setup, find_packages

setup(
    name="csv_to_ddl",
    version="0.1.0",
    packages=find_packages(where="csv_to_ddl"),
    package_dir={"": "csv_to_ddl"},
    install_requires=[],
)