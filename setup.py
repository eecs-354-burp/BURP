from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

setup(
  name = 'BURP',
  version = '0.1',
  packages = find_packages(),
  scripts = ['scripts/burp'],
  package_data = {
    '': ['weka/*']
  },
  test_suite = 'burp.html.tests',
  install_requires = [
    'requests>=0.14.2',
    'pyquery>=1.2.4',
    'liac-arff>=1.0'
  ]
)
