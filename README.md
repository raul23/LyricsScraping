# README for LyricsScraping [Work-in-Progress]
## Description
Crawl and scrap lyrics from music webpages. For the moment, only
[one lyrics website](https://bit.ly/2k5r0SX) is supported. But I will
eventually support another lyrics website that provides an API for easy
retrieval of useful data.

## Dependencies
* **Platforms:** macOS, Linux, Windows
* `Python`: 3.5, 3.6, 3.7
* `BeautifulSoup` : used for parsing the lyrics webpages
* `requests` : used for requesting the HTML content of lyrics webpages
* `yaml` : used for reading configuration files (e.g. logging)
* `py-common-utils` : is a Python toolbox with useful functions and
  modules ready to be used in different projects. For instance, you will
  find code related to databases and logging.


## Installation instructions
1. Download the
   [LyicsScraping](https://github.com/raul23/LyricsScraping) and
   [py-common-utils](https://github.com/raul23/py-common-utils)
   libraries
2. ...

## Usage
These are the two ways to use the `lyrics-scrapers` library:
1. Run the `scraper` script
1. Use the library as API in your own code

### Run the main script
Change directory to `script/` and run the script:  
`python run_scraper.py -c`

**Notes:**
* The option `-c` is for adding color to log messages. 

### Use the library in your own code
