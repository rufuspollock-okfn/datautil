from setuptools import setup, find_packages

import sys
sys.path.insert(0, '.')
from swiss import __version__, __doc__ as __long_description__

setup(
    name='swiss',
    version=__version__,
    license='MIT',
    description='Swiss Army Knife for Data Work',
    long_description=__long_description__,
    author='Open Knowledge Foundation',
    author_email='info@okfn.org',
    url='http://knowledgeforge.net/okfn/swiss/',
    download_url='http://knowledgeforge.net/okfn/swiss/',
    install_requires=[
        'python-dateutil>=1.0',
        # (optional) for excel handling
        # xlrd
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
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
