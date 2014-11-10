from setuptools import setup, find_packages

import sys
sys.path.insert(0, '.')
from datautil import __version__, __doc__ as __long_description__

setup(
    name='datautil',
    version=__version__,
    license='MIT',
    description='Utilities for Data Work',
    long_description=__long_description__,
    author='Open Knowledge Foundation',
    author_email='info@okfn.org',
    url='http://okfn.org/projects/datautil/',
    download_url='https://github.com/okfn/datautil/',
    install_requires=[
        # python-dateutil 2.0 has different _parse method, so stick to 1.4.1
        'python-dateutil>=1.0,<1.99',
        # (optional) for excel handling
        # xlrd
        # (optional) for google docs handling
        # gdata
        ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2 :: Only',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
