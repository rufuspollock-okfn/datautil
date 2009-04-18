from setuptools import setup, find_packages

import sys
sys.path.insert(0, '.')
from swiss import __version__

setup(
    name='Swiss Army Knife',
    version=__version__,
    license='MIT',
    description='Swiss Army Knife for Data Work',
    long_description='''Swiss Army Knife for Data Work''',
    author='Open Knowledge Foundation',
    author_email='info@okfn.org',
    url='http://www.okfn.org/p/swiss/',
    install_requires=[
        'python-dateutil>=1.0',
        ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
