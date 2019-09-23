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
        'Programming Language :: Python',
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
          'pyyaml',
          'requests',
          'py-common-utils @ https://github.com/raul23/py-common-utils/tarball/master'
      ],
      entry_points={
          'console_scripts': ['edit_cfg=bin.edit_cfg:main',
                              'reset_cfg=bin.reset_cfg:main',
                              'run_scraper=bin.run_scraper:main']
      },
      zip_safe=False)
