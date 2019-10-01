"""Module that ...

"""
import re
# Third-party modules
from bs4 import BeautifulSoup


API_HTML_FILEPATH = "_build/html/api_reference.html"


def read_file(filepath):
    """

    Parameters
    ----------
    filepath

    Returns
    -------

    """
    with open(filepath, 'r') as f:
        return f.read()


def write_file(filepath, data):
    """

    Parameters
    ----------
    filepath
    data

    """
    with open(filepath, 'w') as f:
        f.write(data)


def find_dd_tag(id_, filepath=None, soup=None):
    """

    Parameters
    ----------
    filepath : str
    id_ : str

    Returns
    -------
    list
    None

    """
    if soup is None:
        assert filepath
        html = read_file(filepath)
        soup = BeautifulSoup(html, 'lxml')
    dt_tag = soup.find("dt", id=id_)
    dd_tag = dt_tag.find_next_sibling()
    return soup, dd_tag


def replace_hrefs(soup, replacements):
    """TODO

    Parameters
    ----------
    soup : bs4.BeautifulSoup
    replacements : list of dict

    Returns
    -------
    soup : bs4.BeautifulSoup

    """

    def replace_href(pattern, replace_with):
        """TODO

        Parameters
        ----------
        pattern : str or re.Pattern
        replace_with : str

        """
        anchors = soup.find_all("a", href=pattern)
        for a in anchors:
            a.attrs['href'] = replace_with

    for rep in replacements:
        replace_href(
            pattern=rep['pattern'],
            replace_with=rep['replace_with'])
    return soup


def copy_dd_tag():
    """Copy LyricsScraper's <dd> tag to AZLyricsScraper section.

    More specifically, it's the LyricsScraper's <dd> tag associated with
    `scraped_data` definition where its detailed structure is shown that will
    be copied into the AZLyricsScraper section.

    Returns
    -------
    soup : bs4.BeautifulSoup
    None

    """
    # TODO: specify that this id refers to the <dt> tag before where the <dd>
    # will be copied
    source_id = "scrapers.lyrics_scraper.LyricsScraper.scraped_data"
    target_id = "scrapers.azlyrics_scraper.AZLyricsScraper.scraped_data"
    # Get the <dd> tag associated with the `scraped_data` definition where its
    # detailed structure is shown. This <dd> tag is to be found in the
    # LyricsScraper section. This <dd> tag will then be copied into the
    # AZLyricsScraper section
    whole_soup, source_dd_tag_soup = find_dd_tag(source_id,
                                                 filepath=API_HTML_FILEPATH)
    # TODO: Explain ...
    copy_source_dd_tag_soup = BeautifulSoup(str(source_dd_tag_soup), 'lxml')
    copy_source_dd_tag_soup = copy_source_dd_tag_soup.find("dd")
    if copy_source_dd_tag_soup:
        # =================================================
        # Fix paragraph's id associated with `scraped_data`
        # =================================================
        # Fix the the id in the <dd> tag that labels a paragraph associated with
        # the description of `scraped_data`
        # NOTE: the AZLyricsScraper section has a paragraph identified with the
        # id 'scraped-data-label-2' to differentiate it from LyricsScraper's
        # 'scraped-data-label'
        copy_source_dd_tag_soup.find("p", id="scraped-data-label").attrs['id'] \
            = "scraped-data-label-2"
        # =======================================
        # Fix URLs in the AZLyricsScraper section
        # =======================================
        # Some of these URLs point to the `scraped_data` in the LyricsScraper
        # section and we want them to link to the `scraped_data` in the
        # AZLyricsScraper section
        #
        # Here, we define the patterns that will be used to extract the <a> tags
        # that will be replaced by the correct URLs
        # NOTE: you need to escape the dots in the pattern since the pattern is
        # a regex and you don't want the dot to represent any character, but the
        # dot itself
        href_replacements = [
            {'pattern': re.compile("scraped-data-label$"),
             'replace_with': '#scraped-data-label-2'
             },
            {'pattern': re.compile("\.LyricsScraper\.scraped_data$"),
             'replace_with': '#scrapers.azlyrics_scraper.AZLyricsScraper.'
                             'scraped_data'
             }
        ]
        # Get the HTML associated only with the AZLyricsScraper section since
        # we want to change the URLs found only in this section
        azlyrics_soup = whole_soup.find(id="module-scrapers.azlyrics_scraper",
                                        class_="section")
        # Do the URL replacements in the AZLyricsScraper section
        replace_hrefs(azlyrics_soup, href_replacements)
        # ==================================================
        # Copy the <dd> tag into the AZLyricsScraper section
        # ==================================================
        # Find the <dd> tag in the AZLyricsScraper section where we will copy
        soup, target_dd_tag_soup = find_dd_tag(id_=target_id,
                                               soup=azlyrics_soup)
        # Do the copying
        target_dd_tag_soup.replaceWith(copy_source_dd_tag_soup)
    return whole_soup


def post_process(app, exception):
    """Process HTML files generated after the build process.

    This function is called when the `build-finished` event is emitted after the
    build has finished, before Sphinx exits.

    The `api_reference.html` file is processed in order to copy content to some
    other parts of the HTML file, and to fix some links.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        The Sphinx application object.
    exception : Exception
        The `build-finished` event is emitted even when the build process raised
        an exception. See Sphinx's doc on `build-finished
        <https://bit.ly/2o3aynS>`_.

    """
    # ========================================================================
    # OPERATION 1: Copy LyricsScraper's detailed description of `scraped_data`
    #              structure to AZLyricsScraper section
    # ========================================================================
    soup = copy_dd_tag()
    # =======================================================================
    # OPERATION 2: Add link in the 'Bases' part of the AZLyricsScrape section
    # =======================================================================
    # Define a new anchor tag that will be used to add link in the 'Bases' part
    # of the AZLyricsScraper section
    new_tag = "<a class='reference external' href='#scrapers.lyrics_scraper." \
              "LyricsScraper' title='scrapers.lyrics_scraper.LyricsScraper'>" \
              "<code class='xref py py-class docutils literal notranslate'>" \
              "<span class='pre'>scrapers.lyrics_scraper.LyricsScraper</span>" \
              "</code></a>"
    dt_tag = soup.find("dt", id="scrapers.azlyrics_scraper.AZLyricsScraper")
    dd_tag = dt_tag.find_next_sibling()
    dd_tag.p.code.replace_with(BeautifulSoup(new_tag, 'lxml').a)
    # ==============================
    # Save the modified HTML to disk
    # ==============================
    write_file(API_HTML_FILEPATH, str(soup))
