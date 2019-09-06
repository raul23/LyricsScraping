# lyrics-scrapers
## Description
Crawl and scrap lyrics websites. For the moment, only [one site](https://bit.ly/2k5r0SX) 
is supported. But I will eventually support another lyrics website that provides 
an API for easy retrieval of useful data about a song.

## Folders description
* `database/` : SQL schema for creating the database that stores the relevant
scraped data such as the artist's name, the song's title, and more importantly
the song's lyrics.
* `scrapers/` : where the scrapers for the different lyrics websites are defined.
* `script/` : the main script for starting the scraping of the lyrics websites.

## Dependencies
* `Python 3.7`
* `BeautifulSoup` : for parsing the lyrics webpage
* `requests` : for requesting the HTML content of a lyrics webpage
* `yaml` : for reading configuration files (e.g. logging)

## Set environment variables
Add paths to the [utilities](https://github.com/raul23/utilities) and 
[lyrics-scrapers](https://github.com/raul23/lyrics-scrapers) libraries in your 
environment variables:
```commandline
export PYTHONPATH=~/path/to/utilities:$PYTHONPATH
export PYTHONPATH=~/path/to/lyrics-scrapers:$PYTHONPATH
``` 
* [utilities](https://github.com/raul23/utilities) is a Python toolbox with 
useful functions and modules ready to be used in different projects. For instance,
you will find code related to databases and logging.

## Run main script
Change directory to `script/` and run the script:  
`python run_scraper.py -c`

Notes:
* The option `-c` is for adding color to log messages. 
* If you are working with the PyCharm terminal, user the option `-c p` which 
will use colors suitable for this type of terminal which displays color 
differently than a standard Unix terminal.
