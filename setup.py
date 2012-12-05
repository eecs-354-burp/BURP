from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

setup(
  name = 'BURP-HTML',
  version = '0.1',
  packages = find_packages(),
  scripts = ['burp-html'],
  test_suite = 'burp_html.tests',
  install_requires = ['pyquery>=1.2.4']
)
