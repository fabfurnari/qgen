from setuptools import setup, find_packages

setup(
    name='qgen',
    version='0.1',
    description='Simple MySQL pseudo-random query generator',
    author='Fabrizio Furnari',
    author_email='fabfur@fabfur.it',
    package_dir={'': 'qgen'},
    packages=find_packages('qgen',exclude=['docs']),
    package_data={'qgen':'*.json'},
    exclude_package_data = { '': ['README.rst'] },
    license='GPL',
    scripts=['qgen-sample-client.py'],
    install_requires=['Jinja2==2.8',
                      'MarkupSafe==0.23',
                      'mysqlclient==1.3.7'],
)
