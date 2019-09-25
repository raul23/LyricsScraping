"""setup.py file for the package `lyrics_scraping`.

The project name is LyricsScraping and the package name is `lyrics_scraping`.

"""

import os
from setuptools import find_packages, setup


# Directory of this file
dirpath = os.path.abspath(os.path.dirname(__file__))

# The text of the README file
with open(os.path.join(dirpath, "README.md")) as f:
    README = f.read()

setup(name='LyricsScraping',
      version='1.0',
      description='Crawl and scrap lyrics from song webpages',
      long_description=README,
      long_description_content_type='text/markdown',
      classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries'
      ],
      keywords='lyrics web scraping python',
      url='https://github.com/raul23/LyricsScraping',
      author='Raul C.',
      author_email='rchfe23@gmail.com',
      license='GPLv3',
      packages=find_packages(exclude=['tests']),
      include_package_data=True,
      install_requires=[
          'beautifulsoup4',
          'lxml',
          'm2r',
          'pyyaml',
          'requests',
          'sphinx_rtd_theme',
          'py-common-utils @ https://github.com/raul23/py-common-utils/tarball/master'
      ],
      entry_points={
          'console_scripts': ['scraper=bin.scraper:main']
      },
      zip_safe=False)
