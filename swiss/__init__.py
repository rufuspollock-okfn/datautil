'''Swiss Army Knife for Data Work
==============================

The swiss package provides various utilities for working with data:

  * cache: Url caching and scraping
  * tabular/*: Processing and transforming tabular data to and from various
    formats including csv, json, google spreadsheets, xls
  * misc, date: Cleaning up and parsing data especially dates.
  * id: ID generation and shortenening
  * clitools.py: Command line tools such as creating optparse object and usage
    from a module of object.
  * deliveranceproxy.py: Deliverance proxy helper


CHANGELOG
=========

v0.3 2010-??-??
---------------

  * Support for google docs spreadsheets as sources for TabularData
  * Improve documentation of date module and add FlexiDate.as_datetime()
  * New clitools module incorporating existing cli tools
  * deliveranceproxy.py: Deliverance proxy helper
  * parse/name.py: new (human) name parsing code

v0.2 2009-10-23
---------------

  * Extensive refactoring of tabular module/package
    * Standardized interface with BaseReader and BaseWriter
    * JsonReader and JsonWriter providing json reading and writing
    * TxtWriter to support writing to plain text
  * Improvements to date parsing (support for circa, 'c.', etc)
  * New id module to do 'compression' of uuids using 32 and 64 bit encoding


v0.1 2009-06-03
---------------

  * Bring together existing code (from last 2+ years) into new 'swiss' package
  * Url caching and scraping
  * Tabular data handling including csv reader/writer, xls reader, latex writer
    and associated utilities (such as pivot_table)
  * Cleaning and parsing data especially dates (misc and date modules)
'''
__version__ = '0.3a'

import tabular
from cache import *
from misc import *
from id import *
