# lyrics-scrapers
## Description
Crawl and scrap lyrics websites.
## Folders description
* `database/` : SQL schema for creating the database that stores the relevant
scraped data such as the artist's name, the song's title, and more importantly
the song's lyrics.
* `scrapers/` : where the scrapers for the different lyrics website are defined.
* `script/` : the main script for starting the scraping of the lyrics websites.
## Dependencies
* `Python 3.7`
* `BeautifulSoup` :
* `yaml` : 
## Set environment variables
Set paths to `utilities` and `lyrics-scrapers` projects in your environment 
variables:
```commandline
export PYTHONPATH=~/path/to/utilities:$PYTHONPATH
export PYTHONPATH=~/path/to/lyrics-scrapers:$PYTHONPATH
``` 
## Run main script
Change directory to `script/` and run the script:  
`python run_scraper.py -c`

Notes:
* The option `-c` is for adding color to log messages. 
* If you are working with the PyCharm terminal, user the option `-c p` which 
will use colors suitable for this type of terminal which display color 
differently than a standard Unix terminal.
