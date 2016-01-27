.. _queries-template:

Queries template
================

The best way to specify a query dictionary to pass to the module is to create a JSON file and load it using `json.loads()`_.

Included in this module you will find a sample configuration file and in the ``sample-client.py`` script the demonstration on how to use it. Feel free to extend and edit as you want.

JSON syntax
-----------

The syntax for the JSON file/dictionary is the following:

.. code-block:: javascript

    {
      "verb": {"weight": int, "queries": ["query1", "query2", ...]},
      "anotherverb": {"weight": int, "queries": ["anotherquery", ...]},
      ...
    }

* ``verb``: a lowercase string choosen from "insert", "update", and so on.
  Is used as index to choose which kind of query should be run.
  You can include as many verb you want (they must be valid SQL verbs, 
  of course) and exclude them from being run in other ways.

* ``weight``: an integer number representing how many query associated with 
  that verb should be run. This is used to build a weighted population from
  which a random one will be picked. If I want, as an example, run just one
  ``UPDATE`` query on ten ``SELECT`` queries I'll set the weight for the two
  verbs appropriately.

* ``queries``: a list of queries with Jinja2 template parameters that will
  be picked and executed.

Jinja2 variables
----------------

The following variables will be replaced when a query is picked and run:

* ``{{ all }}``: is replaced with ``*`` (use for ``SELECT * FROM ...``).
* ``{{ random_table }}``: is replaced with a random table picked from
  the current database schema.
* ``{{ random_column }}``: is replaced with a random column in the 
  ``{{ random_table }}``.
* ``{{ appropriate_value }}``: is replaced with a random value of the 
  ``{{ random_column }}`` type.
* ``{{ second_random_column }}``: is replaced with another random column in
  the same ``{{ random_table }}`` table. Useful when you want to ``UPDATE``
  a column using another column in the ``WHERE`` clause.
* ``{{ random_value }}``: is a simple random value picked from the 
  ``{{ random_column }}`` column.

Example
-------

.. code-block:: guess

    {"select":
       {"weight": 10,
        "queries": ["SELECT {{ all }} FROM {{ random_table }} ...",
         ...]
       },
     "update":
       {"weight": 1,
         ...
       },
      ...
     }

.. _json.loads(): https://docs.python.org/2/library/json.html#json.loads
