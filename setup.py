from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

setup(
  name = 'BURP-URL',
  version = '0.1',
  packages = find_packages(),
  package_data = {
    # If any package contains *.txt files, include them:
    '': ['*.txt'],
	}
)
