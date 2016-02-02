"""QGen module.

Example:
    Very simple QGen module usage

      >>> from qgen import QGen
      >>> queries = json.loads(open('data/queries.json').read())  #Load a dictionary from file (see below for dictionary formatting)
      >>> verbs = ['select','insert'] # Use only SELECT and INSERT verbs
      >>> q = qgen.QGen(db_host='localhost',db_user='someuser',db_pass'somepass', db_name='somename',queries_template=queries,allowed_verbs=verbs)
      >>> q.tables # to inspect the tables schema
      >>> # Start running 100 queries but stop on errors:
      >>> for q in q.batch_run(halt_on_errors=False):
      ...    print(q['last_executed'])


.. module:: qgen
   :platform: Unix
   :synopsis: Simple MySQL "random" query generator

.. moduleauthor:: Fabrizio Furnari <>

"""

# For python 2.x
from __future__ import print_function

import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass
logging.getLogger(__name__).addHandler(NullHandler())

import MySQLdb as mdb
import MySQLdb.cursors as mdb_cursors
from jinja2 import Template
import random
import time
import datetime
import string

from .exceptions import QGenStopException, QGenNoQueriesException

class QGen(object):
    '''Prepare, check and run queries against a MySQL database
    
    Parameters:
        db_host (str, optional): IP address or name for the MySQL host. Defaults to localhost.
        db_user (str): MySQL valid username for the DB.
        db_pass (str): MySQL valid password for the DB.
        db_name (str, optional): MySQL database name. Defaults to db_user
        allowed_verbs (list, optional): A list of allowed SQL verbs to avoid
          potentially dangerous queries. Defauts to ['select']
        queries_template (dict): The queries to be rendered and run
          This must be a dictionary containing the query verbs, their
          weight and the actual queries template in Jinja2 format.

          See the :ref:`queries-template` section for more information on
          how to structure.

    Attributes:
        tables (dict): a tables schema in dictionary form set by the :py:meth:`qgen.QGen._get_tables_schema`
        
    '''
          
    def __init__(self, **kwargs):
        db_host = kwargs['db_host'] or 'localhost'
        db_user = kwargs['db_user']
        db_pass = kwargs['db_pass']
        db_name = kwargs['db_name'] or db_user
        self.queries_template = kwargs['queries_template']
        self.allowed_verbs = kwargs['allowed_verbs'] or ['select']

        try:
            self._con = mdb.connect(db_host,db_user,db_pass,db_name,
                                    cursorclass=mdb_cursors.DictCursor)
            self._cur = self._con.cursor()
            self._cur.execute("USE %s" % db_name)
        except mdb.Error as e:
            logging.critical('Cannot connect to db %s: %s' % (db_name, e))

        self.tables = self._get_tables_schema()

    def _run_query(self, query=None, needs_commit=None, halt_on_errors=None):
        '''Simple wrapper to run queries
        '''
        try:
            self._cur = self._con.cursor()
        except Exception as e:
            logging.critical("Cannot get connection cursor: %s" % e)
            
        res = dict()
        try:
            start = time.time()
            logging.debug("Running query %s, needs_commit: %s" % (query, needs_commit))
            self._cur.execute(query)
        except mdb.Error as e:
            logging.warning("Cannot run query %s: %s, trying rollback ..." % (query, e))
            self._con.rollback()
            logging.warning("Query %s rolled back!" % query)
            res['results_number'] = 0
            res['output'] = None
            if halt_on_errors:
                logging.error("Stopping on error as requested")
                raise QGenStopException
        else:
            if needs_commit:
                res['output'] = self._con.commit()
                logging.debug("Query %s committed: %s" % (query, str(res['output'])))
                res['results_number'] = 0
            else:
                res['output'] = self._cur.fetchall()
                logging.debug("Query output: %s" % str(res['output']))
                res['results_number'] = len(res['output'])
        finally:
            stop = time.time()
            res['elapsed_time'] = round(((stop - start) * 1000), 2)
            res['last_executed'] = self._cur._last_executed
        return res

    def _get_tables_schema(self):
        '''Inspects the DB schema and returns tables and some columns
        information as dict
        '''
        res = self._run_query("SHOW TABLES", needs_commit=None)
        try:
            tables = {list(t.values())[0]: None for t in res['output']}
            for table in tables.keys():
                res = self._run_query("SELECT COLUMN_NAME,DATA_TYPE,COLUMN_KEY FROM information_schema.columns WHERE table_name = '%s'" % table, needs_commit=None)
                tables[table] = { i['COLUMN_NAME']:
                                  {'type': i['DATA_TYPE'],
                                  'is_primary': bool(i['COLUMN_KEY'] == 'PRI')}
                                  for i in res['output']
                                  }
        except mdb.Error as e:
            logging.critical("Cannot get db schema: %s" % e)

        else:
            return tables

    def _get_random_table(self):
        tables = list(self.tables.keys())
        table_name = random.choice(tables)
        return table_name

    def _get_random_column(self, table_name=None):
        columns = list(self.tables[table_name].keys())
        column_name = random.choice(columns)        
        return column_name

    def _get_random_value(self, table_name=None, column_name=None):
        '''
        Gets a random value from a given table and column to be used
        in the WHERE clause and returns it as string.
        This function must be used sparely cause it's slowness.
        '''
        q = "SELECT `{}` FROM `{}` ORDER BY rand() LIMIT 1".format(column_name, table_name)
        res = self._run_query(q, needs_commit=None)
        if not res['output']:
            logging.warning("No output from query %s" % q)
            return None
        values = list(res['output'][0].values())
        return values[0]

    def _get_appropriate_value(self, table_name=None, column_name=None):
        '''
        Return random value of the type determined by the column
        '''
        convert_map = {'smallint': int,
                       'tinyint': int,
                       'mediumint': int,
                       'int': int,
                       'decimal':  float,
                       'varchar': str,
                       'text': str,
                       'char': str,
                       'date': datetime.datetime,
                       'datetime': datetime.datetime,
                       'timestamp': datetime.datetime,
                       'enum': None,
                       'set': None}
        
        column_type = convert_map[self.tables[table_name][column_name]['type']]
        if column_type == int:
            return random.randint(0,100)
        elif column_type == float:
            return random.random()
        elif column_type == str:
            return ''.join(random.choice(string.ascii_lowercase) for i in range(random.randint(1,20)))
        else:
            return None

    def _get_allowed_queries(self):
        '''Compares the queries in the json template with the allowed ones
        and returns only the allowed ones as sub-dict
        '''
        allowed_queries = dict()
        try:
            for k in self.queries_template.keys():
                if k.lower() in self.allowed_verbs:
                    allowed_queries[k] = self.queries_template[k]            
        except Exception as e:
            logging.critical('Cannot get allowed queries: %s', e)
        return allowed_queries

    def pick_query(self):
        '''
        Parameters:
            None

        Returns:
            A tuple in form (verb, query)
        '''
        allowed_queries = self._get_allowed_queries()
        if not allowed_queries:
            raise QGenNoQueriesException

        # Build a list of weighted verbs based on the weight
        # assigned to each query
        population = []
        for v in allowed_queries.keys():
            _i = [v] * self.queries_template[v]['weight']
            population.extend(_i)

        rnd_verb = random.choice(population)
        # At the moment 'insert' is not supported
        if rnd_verb.lower() == 'insert':
            raise NotImplementedError
        # ... and a random query for that verb
        rnd_query = random.choice(allowed_queries[rnd_verb]['queries'])
        return (rnd_verb, rnd_query)

    def valorize_query(self, query):
        '''Inspect the query, get random values and populate it

        Parameters:
            query (str): The query to populate, in Jinja2 template

        Returns:
            The populated query in string format
        '''
        tpl = Template(query)

        # Some random values to populate the template
        random_table = self._get_random_table()
        random_column = self._get_random_column(table_name=random_table)
        if "random_value" in query:
            # Avoids to call the _get_random_value function (expensive)
            # every time
            random_value = None
            while not random_value:
                logging.debug("None is not an acceptable random value, retrying")
                random_table = self._get_random_table()
                random_column = self._get_random_column(table_name=random_table)
                random_value = self._get_random_value(table_name=random_table, column_name=random_column)
        else:
            random_value = None

        if "appropriate_value" in query:
            # Same as before but use new column values to update
            second_random_column = self._get_random_column(table_name=random_table)
            appropriate_value = self._get_appropriate_value(table_name=random_table, column_name=second_random_column)
        else:
            second_random_column = None
            appropriate_value = None

        q = tpl.render({'all':'*',
                        'random_table': random_table,
                        'random_column': random_column,
                        'random_value': random_value,
                        'appropriate_value': appropriate_value,
                        'second_random_column': second_random_column})
        return q

    
    def batch_run(self, max_queries=10, interval=1, halt_on_errors=None, dry_run=False):
        '''Actually run queries

        Arguments:
            max_queries (int, optional): number of queries to run before stop. Defaults to 10.
            interval (float, optional): interval in seconds between each query. Defaults to 1 second.
            halt_on_errors (bool, optional): set to True to stop if a query
              fails. Defaults to None.
            dry_run (bool, optional): no not really run queries, just log and return fake results. Defaults to None.

        Yields:
            dict: a dictionary with query information
        
        '''
        res = {'results_number': None, 'output': None, 'last_executed': None, 'elapsed_time': None}
        total_start_time = time.time()
        for i in range(1,max_queries):
            rnd_verb, q = self.pick_query()
            needs_commit = None if rnd_verb.lower() == 'select' else True
            query = self.valorize_query(query=q)
            if not dry_run:
                try:
                    res = self._run_query(query, needs_commit, halt_on_errors)
                except QGenStopException as e:
                    res['last_executed'] = query
                    return
            else:
                logging.debug("NOT running query %s (dry-run mode)" % query)
                res['last_executed'] = query
                yield res
            
            status = "Query: {}; Results number: {}; Elapsed time: {} ms".format(res['last_executed'], res['results_number'], res['elapsed_time'])
            logging.info(status)
            yield res
            time.sleep(interval)

        total_stop_time = time.time()
        total_elapsed_time = round((total_stop_time - total_start_time), 2)
        logging.info("Total time elapsed: %s s" % total_elapsed_time)

