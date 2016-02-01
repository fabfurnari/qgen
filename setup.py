from setuptools import setup

from os import path
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst')) as f:
    long_description = f.read()

setup(
    name='qgen',
    version='0.1',
    url='https://github.com/fabfurnari/qgen',
    description='Simple MySQL pseudo-random query generator',
    long_description=long_description,
    author='Fabrizio Furnari',
    author_email='fabfur@fabfur.it',
    packages=['qgen'],
    package_data={'data':['*.json']},
    exclude_package_data = {'': ['README.rst'] },
    license='GPL',
    scripts=['qgen-sample-client.py'],
    install_requires=['Jinja2==2.8',
                      'MarkupSafe==0.23',
                      'mysqlclient==1.3.7'],
)
