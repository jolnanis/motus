from setuptools import setup, find_packages

setup(
    name='motus',
    version='0.0.1',
    packages=find_packages(exclude=('tests', 'tests.*')),
)
