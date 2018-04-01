
from setuptools import find_packages, setup
setup(
  name = "fastscore-cli",
  description = "FastScore CLI",
  version = "1.7.3",
  packages = find_packages(),
  use_2to3=True,

  install_requires = [
    "iso8601>=0.1.11",
    "PyYAML>=3.11",
    "requests>=2.11.1",
    "tabulate>=0.7.5",
    "websocket-client>=0.37.0",
    "urllib3 >= 1.2",
    "certifi >= 2017.4.17",
    "avro >= 1.7.6",
    "parse >= 1.8.2"
  ],

  entry_points = {
    "console_scripts": [ "fastscore=cli.dispatch:main" ]
  },

  data_files = [
    ('/etc/bash_completion.d/', ['extra/fastscore']),
  ]
)

