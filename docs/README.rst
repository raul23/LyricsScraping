=========================
README [Work-in-Progress]
=========================
.. raw:: html

   <p align="center"><img src="https://raw.githubusercontent.com/raul23/LyricsScraping/master/docs/_static/images/LyricsScraping_logo.png"></p>

.. image:: https://readthedocs.org/projects/lyricsscraping/badge/?version=latest
   :target: https://lyricsscraping.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation Status

**LyricsScraping** crawls and scraps lyrics from AZLyrics.

.. contents::
   :local:

Dependencies
============
* **Platforms:** macOS, Linux, Windows
* **Python**: 3.5, 3.6, 3.7
* ``BeautifulSoup`` : used for crawling and parsing the lyrics webpages
* ``requests`` : used for requesting the HTML content of lyrics webpages
* ``yaml`` : used for reading configuration files (e.g. logging)
* ``py-common-utils`` : is a Python collection of utilities with useful functions and modules
  ready to be used in different projects. For instance, you will find code
  related to databases and logging.

Installation instructions
=========================
1. Download the `LyicsScraping <https://github.com/raul23/LyricsScraping>`_ and
   `py-common-utils <https://github.com/raul23/py-common-utils>`_ libraries
2. ...

Usage
=====
These are the two ways to use the ``lyrics-scraping`` package:

#. Run the ``scraper`` script
#. Use the library as API in your own code

Run the main script
-------------------
Run the script with::

    $ python run_scraper.py -c

**Note:**

* The option ``-c`` is for adding color to log messages.

Use the library in your own code
--------------------------------
