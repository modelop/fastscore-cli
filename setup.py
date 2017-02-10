
from setuptools import find_packages, setup
setup(
  name = "fastscore-cli",
  description = "FastScore CLI",
  version = "dev",
  packages = find_packages(),

  install_requires = [
    "iso8601==0.1.11",
    "PyYAML==3.11",
    "requests==2.11.1",
    "tabulate==0.7.5",
    "websocket-client==0.37.0"
  ],

  entry_points = {
    "console_scripts": [ "fastscore=fastscore.dispatch:main" ]
  },

  data_files = [
    ('/etc/bash_completion.d/', ['extra/fastscore']),
  ]
)

