#!/usr/bin/env python

import logging
from qgen import QGen
import sys
import os
import json
import argparse

# get configuration somewere
parser = argparse.ArgumentParser(description='Simple QGen client')
parser.add_argument('--host',required=False,default=os.environ.get('QGEN_DB_HOST', 'localhost'), help='The database host')
parser.add_argument('--username',default=os.environ.get('QGEN_DB_USER', 'employees'), required=False, help='The database username')
parser.add_argument('--password',default=os.environ.get('QGEN_DB_PASS', 'password'), required=False, help='The database password')
parser.add_argument('--dbname',default=os.environ.get('QGEN_DB_NAME', 'employees'), required=False, help='The database name')
parser.add_argument('--queries',default=os.environ.get('QGEN_TEMPLATE_FILE', 'data/queries.json'), required=False, help='The queries template file')
parser.add_argument('--verbs',nargs='+', required=False, help='List of space-separated verbs like select, insert, update and so on')
parser.add_argument('--dry-run',action='store_true',default=None, help='Do not really execute queries')
parser.add_argument('--loglevel',default='INFO',required=False,choices=['DEBUG','INFO','WARNING','ERROR','CRITICAL'], help='Log level')
parser.add_argument('--stop',action='store_true',default=False, help='Stop immediately on query error')
args = parser.parse_args()

logging.basicConfig(format='%(levelname)s:%(message)s', level=getattr(logging, args.loglevel))

try:
    f = open(args.queries)
except IOError as e:
    logging.critical('Cannot open query template file %s: %s' % (args.queries, e))
    sys.exit(1)
try:
    queries_template = json.loads(f.read())
except Exception as e:
    logging.critical("Cannot load query template: %s" % e)
    sys.exit(1)

try:
    q = QGen(db_host=args.host,
             db_user=args.username,
             db_pass=args.password,
             db_name=args.dbname,
             queries_template=queries_template,
             allowed_verbs=args.verbs)
except Exception as e:
    logging.critical("Cannot connect to db %s: %s" % (args.dbname, e))
    sys.exit(1)
    
try:
    for q in q.batch_run(halt_on_errors=args.stop, dry_run=args.dry_run):
        print(q['last_executed'])
        print(q['elapsed_time'])
except Exception as e:
    logging.critical("Cannot perform query: %s" % e)
    sys.exit(1)
