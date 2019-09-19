# lyrics-scrapers [Work-in-Progress]
## Description
Crawl and scrap lyrics from webpages. For the moment, only 
[one lyrics website](https://bit.ly/2k5r0SX) is supported. But I will 
eventually support another lyrics website that provides an API for easy 
retrieval of useful data about a song.

## Folders description
* `examples/` : 
* `music_database/` : contains the SQL schema for creating the database that 
stores the relevant scraped data such as the artist's name, the song's title, 
and more importantly the song's lyrics.
* `scrapers/` : Python package where the scrapers for the different lyrics 
websites are defined.
* `script/` : contains the main script for starting the scraping of lyrics
webpages.

## Dependencies
* `Python 3.7`
* `BeautifulSoup` : used for parsing the lyrics webpages
* `requests` : used for requesting the HTML content of lyrics webpages
* `yaml` : used for reading configuration files (e.g. logging)
* `utilities` : custom library that ...

## Installation instructions
1. Download the [lyrics-scrapers](https://github.com/raul23/lyrics-scrapers) 
and [utilities](https://github.com/raul23/utilities) libraries
1. Set environment variables
1. ...
### Set environment variables
Add paths to the [lyrics-scrapers](https://github.com/raul23/lyrics-scrapers) 
and [utilities](https://github.com/raul23/utilities) libraries in your environment 
variables:
```commandline
export PYTHONPATH=~/path/to/lyrics-scrapers:$PYTHONPATH
export PYTHONPATH=~/path/to/utilities:$PYTHONPATH
``` 
* [utilities](https://github.com/raul23/utilities) is a Python toolbox with 
useful functions and modules ready to be used in different projects. For 
instance, you will find code related to databases and logging.

## Usage
These are the two ways to use the `lyrics-scrapers` library:
1. Run the main script 
1. Use the library as API in your own code

### Run the main script
Change directory to `script/` and run the script:  
`python run_scraper.py -c`

**Notes:**
* The option `-c` is for adding color to log messages. 
* If you are working with the PyCharm terminal, use the option `-c p` which 
will use colors suitable for this type of terminal which displays color 
differently than a standard Unix terminal.

### Use the library as API in your own code
