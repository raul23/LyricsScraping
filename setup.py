"""setup.py file for the package `lyrics_scraping`.

The project name is LyricsScraping and the package name is `lyrics_scraping`.

"""

import os
from setuptools import setup

# The text of the README file
with open(os.path.join(os.getcwd(), "README.md")) as f:
    README = f.read()

setup(name='LyricsScraping',
      version='1.0',
      description='Crawl and scrap lyrics from song webpages',
      long_description=README,
      long_description_content_type='text/markdown',
      classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries'
      ],
      keywords='lyrics web scraping python',
      url='https://github.com/raul23/LyricsScraping',
      author='Raul C.',
      author_email='rchfe23@gmail.com',
      license='MIT',
      packages=['lyrics_scraping'],
      include_package_data=True,
      install_requires=[
          'beautifulsoup4',
          'lxml',
          'pyyaml',
          'py-common-utils @ https://github.com/raul23/py-common-utils/tarball/master'
      ],
      entry_points={
          'console_scripts': [
              'lyricsgenius = lyricsgenius.__main__:main']
      },
      zip_safe=False)
