from setuptools import find_packages, setup
import versioneer

setup(
  name = "fastscore-cli",
  version=versioneer.get_version(),
  cmdclass=versioneer.get_cmdclass(),
  description = "FastScore CLI",
  packages=find_packages(),
  use_2to3=True,

  install_requires = [
    "fastscore>=1.6.1",
    "avro>=1.7.6",
    "parse>=1.8.2"
  ],

  entry_points = {
    "console_scripts": [ "fastscore=cli.dispatch:main" ]
  },

  data_files = [
    ('/etc/bash_completion.d/', ['extra/fastscore']),
  ]
)
