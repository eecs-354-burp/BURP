from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

setup(
  name = 'burphtml',
  version = '0.1',
  packages = find_packages(),
  test_suite = 'burphtml.tests',
  install_requires = ['pyquery>=1.2.4']
)

