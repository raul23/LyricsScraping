from setuptools import setup

setup(name='lyrics_scraping',
      version='0.1',
      description='Crawl and scrap lyrics from webpages',
      long_description='Crawl and scrap lyrics from webpages.',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries'
      ],
      keywords='web lyrics scraping python',
      url='https://github.com/raul23/lyrics-scrapers',
      author='Raul C.',
      author_email='rchfe23@gmail.com',
      license='MIT',
      packages=['music_database', 'scrapers', 'script'],
      include_package_data=True,
      install_requires=[
          'beautifulsoup4',
          'lxml',
          'pyyaml',
          'utilities @ https://github.com/raul23/utilities/tarball/master'
      ],
      scripts=['script/run_scraper.py'],
      zip_safe=False)
