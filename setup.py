
from setuptools import find_packages, setup
setup(
  name = "fastscore-cli",
  description = "FastScore CLI",
  version = "dev",
  packages = find_packages(),
  use_2to3=True,

  install_requires = [
    "iso8601==0.1.11",
    "PyYAML==3.11",
    "tabulate==0.7.5",
    "websocket-client==0.37.0",
    "urllib3 >= 1.15",
    "certifi >= 14.05.14",
    "avro >= 1.7.6"
  ],

  entry_points = {
    "console_scripts": [ "fastscore=cli.dispatch:main" ]
  },

  data_files = [
    ('/etc/bash_completion.d/', ['extra/fastscore']),
  ]
)

