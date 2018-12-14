.. FastScore SDK documentation master file, created by
   sphinx-quickstart on Sat May  6 22:30:29 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

FastScore SDK for Python
========================

Release |version|

An example of an interaction with FastScore::

  >>> import fastscore
  >>> connect = fastscore.Connect("https://localhost:8000")
  >>> model = fastscore.Model('model-1')
  >>> model.source = '...'
  >>> mm = connect.lookup('model-manage')
  >>> model.update(mm)
  >>> mm.models.names()
  ['model-1']
  >>> del mm.models['model-1']

The User Guide
--------------

.. toctree::
   :maxdepth: 2

   user/intro
   user/install
   user/advanced

The API documentation / Guide
-----------------------------

.. toctree::
  :maxdepth: 2

  api

The Developer Guide
-------------------

.. toctree::
   :maxdepth: 2

   dev/todo

