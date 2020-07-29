"""setup.py file for the package `lyrics_scraping`.

The project name is LyricsScraping and the package name is `lyrics_scraping`.

"""

import os
from setuptools import find_packages, setup


# Directory of this file
dirpath = os.path.abspath(os.path.dirname(__file__))

# The text of the README file
with open(os.path.join(dirpath, "README.rst")) as f:
    README = f.read()

# TODO: get the version programmatically
setup(name='LyricsScraping',
      version='0.1',
      description='Crawl and scrap lyrics from song webpages',
      long_description=README,
      long_description_content_type='text/x-rst',
      classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
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
          'pyyaml',
          'requests',
          'py-common-utils @ https://github.com/raul23/py-common-utils/tarball/master'
      ],
      entry_points={
          'console_scripts': ['scraper=lyrics_scraping.scripts.scraping:main']
      },
      zip_safe=False)
