'''Swiss Army Knife for Data Work.

The swiss package provides various utilities for working with data:

  * Url caching and scraping
    * cache module
  * Processing and transforming tabular data to and from various formats.
    * tabular module
  * Cleaning up and parsing data.
    * misc and date modules
'''
__version__ = '0.1'

from tabular import *
from cache import *
from misc import *
