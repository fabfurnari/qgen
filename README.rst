Introduction
============

``query-generator`` (**qgen**) is a templating and generation system to run random query against a MySQL data to simulate workload and for other testing tasks.

It tries to be as simple and standard as possible, without unneeded dependencies.

.. warning:: THIS MODULE IS STILL AN ALPHA VERSION. PLEASE DO NOT USE IT UNTIL YOU DON'T KNOW EXACTLY WHAT YOU DO!

What is
-------

* A simple "plug and run" module to generate pseudo-random traffic on a MySQL db, useful to test replicas and failover
* An exercise for me to write Python3 script and put hands on some code

What is not
-----------

* A stress test utility
* A performance tool

Dependencies
------------

* `mysqlclient`_ package (depends on the ``libmysqlclient-dev`` debian package)

Sample usage
------------

.. warning:: **THIS SCRIPT WILL BREAK YOUR DATABASE!** Please consider using a test db to load first into your MySQL instance such as https://github.com/datacharmer/test_db

Using the **sample-client.py** script in the top folder is very easy. You can edit and place your connection parameters inside the script or use arguments:

.. code-block:: bash

  $ python sample-client.py --host localhost \ 
  >                         --username testuser \
  >                         --password testpassword \
  >                         --dbname testdb \
  >                         --queries data/queries.json \ 
  >                         --verbs select

To use also the ``UPDATE`` and ``DELETE`` verbs (**THIS WILL ALTER DATA IN YOUR DATABASE!**)

.. code-block:: bash

  $ python sample-client.py --verbs update delete

Or you can choose to not actually run, just print queries:

.. code-block:: bash

  $ python sample-client.py --dry-run

Or to stop execution after an error

.. code-block:: bash

  $ python sample-client.py --stop --verbs update

Or alternatively you can user evironment variables: 

.. code-block:: bash

  $ QGEN_DB_HOST=192.168.6.60 QGEN_DB_USER=employees QGEN_DB_PASS=password QGEN_DB_NAME=employees QGEN_TEMPLATE_FILE=data/queries.json python sample-client.py

See ``sample-client.py --help`` to obtain more information about usage.

IDEAS/TODO
----------

* Add configuration file option to sample client
* Test with python3
* Add setup for eggs/wheels

.. _mysqlclient: https://pypi.python.org/pypi/mysqlclient
