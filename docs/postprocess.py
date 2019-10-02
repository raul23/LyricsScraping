"""Module that defines functions used with `build-finished`.

`build-finished` event is emitted after the build has finished, before Sphinx
exits.

See Also
--------
process_docstring : a module that defines functions used with
                    `autodoc-process-docstring`.

References
----------
.. [1] `build-finished <https://bit.ly/2o3aynS>`_.

.. _Beautiful Soup Documentation (Quick Start): https://bit.ly/2kzsNzW

"""
import re
# Third-party modules
from bs4 import BeautifulSoup


API_HTML_FILEPATH = "_build/html/api_reference.html"


def read_file(filepath):
    """Read a file from disk.

    Parameters
    ----------
    filepath : str
        Path to the file to be read from disk.

    Returns
    -------
    str
        Content of the file returned as strings.

    """
    with open(filepath, 'r') as f:
        return f.read()


def write_file(filepath, data):
    """Write data to a file.

    Parameters
    ----------
    filepath : str
        Path to the file where the data will be written.
    data :
        Data to be written.

    """
    with open(filepath, 'w') as f:
        f.write(data)


def find_dd_tag(id_, filepath=None, soup=None):
    """Find a <dd> tag in an HTML document.

    We make use of the <dt> that is a top sibling to the <dd> tag in order to
    find the given <dd> tag. This <dt> tag is identified with an `id_`.

    The reason to use the <dt> tag is because the actual <dd> tag doesn't have
    any id associated with it that could have easily distinguished it from the
    other <dd> tags in the HTML document.

    Parameters
    ----------
    filepath : str
        The path to the HTML document.
    id_ : str
        The id of the <dt> tag that is the top sibling to the <dd> tag.

    Returns
    -------
    tuple : (bs4.BeautifulSoup, bs4.BeautifulSoup)
        The first element in the tuple refers to the whole HTML document where
        the search of the <dd> tag was performed, and the second element refers
        to the found <dd> tag.

    Notes
    -----
    If no `filepath` is given, then the BeautifulSoup object associated with
    the HTML document will be used. This can be useful in that we don't have to
    re-open the HTML file.

    """
    if soup is None:
        assert filepath, "Since no filepath to the HMTL document was given, a " \
                         "BeautifulSoup object is needed but was not provided."
        html = read_file(filepath)
        soup = BeautifulSoup(html, 'lxml')
    # Find first the <dt> tag who is a top sibling to the actual <dd> tag
    dt_tag = soup.find("dt", id=id_)
    # Get to the <dd> tag who is the next sibling to the <dt> tag
    dd_tag = dt_tag.find_next_sibling()
    return soup, dd_tag


def replace_hrefs(soup, replacements):
    """Replace URLs in an HTML document with new ones.

    Parameters
    ----------
    soup : bs4.BeautifulSoup
        BeautifulSoup object that will be updated.
    replacements : list of dict
        Used to do the replacements of the URLs in the HTML document.

        Each item in the list refers to a dictionary. This dictionary specifies
        the pattern to use to find the URL to be replaced, and the new URL.

        Its keys and values are defined as follow:
            .. code:: python

                replacements = [
                    {
                        'pattern': "pattern here",
                        'replace_with': "replacement here"
                    }
                ]

    Returns
    -------
    soup : bs4.BeautifulSoup
        BeautifulSoup object that contains the updated URLs.

    """

    def replace_href(pattern, replace_with):
        """Replace a single URL in the HTML document.

        Parameters
        ----------
        pattern : str or re.Pattern
            The whole URL to be replaced or the pattern as a regex which will
            be used to get the URL to be replaced.
        replace_with : str
            The URL that will replaced the old one.

        """
        # There can be lots of <a> tags that satisfies the given pattern and
        # they must be all replaced
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

    More specifically, it's the LyricsScraper's <dd> tag associated with the
    `scraped_data` definition where its detailed structure is shown that will
    be copied into the AZLyricsScraper section.

    Returns
    -------
    whole_soup : bs4.BeautifulSoup
        The HTML associated with the whole **updated** HTML document is returned
        as a BeautifulSoup object, which represents the document as a nested
        data structure (See `Beautiful Soup Documentation (Quick Start)`_).

        This BeautifulSoup object can then be further updated with other kind
        of operations.

    """
    # These are the ids of the <dt> tag before the <dd> tag where the
    # `scraped_data` description is to be found in the LyricsScraper (source)
    # and the AZLyricsScraper (target) sections
    source_id = "scrapers.lyrics_scraper.LyricsScraper.scraped_data"
    target_id = "scrapers.azlyrics_scraper.AZLyricsScraper.scraped_data"
    # Get the <dd> tag associated with the `scraped_data` definition where its
    # detailed structure is shown. This <dd> tag is to be found in the
    # LyricsScraper section. This <dd> tag will then be copied into the
    # AZLyricsScraper section
    whole_soup, source_dd_tag_soup = find_dd_tag(source_id,
                                                 filepath=API_HTML_FILEPATH)
    # I need to make a copy of the <dd> tag from the LyricsScraper because if I
    # don't, all the changes I will be doing on this <dd> tag will also be
    # reflected in the <dd> tag from the LyricsScraper section, and I just want
    # those changes to be associated with the AZLyricsScraper section.
    copy_source_dd_tag_soup = BeautifulSoup(str(source_dd_tag_soup), 'lxml')
    copy_source_dd_tag_soup = copy_source_dd_tag_soup.find("dd")
    if copy_source_dd_tag_soup:
        # Some preprocessing must be done on the <dd> tag to be copied and the
        # HTML associated with the AZLyricsScraper section
        # ==================================================================
        # PREPROCESSING 1: Fix paragraph's id associated with `scraped_data`
        # ==================================================================
        # Fix the the id in the <dd> tag that labels a paragraph associated with
        # the description of `scraped_data`
        # NOTE: the AZLyricsScraper section has a paragraph identified with the
        # id 'scraped-data-label-2' to differentiate it from LyricsScraper's
        # 'scraped-data-label'
        copy_source_dd_tag_soup.find("p", id="scraped-data-label").attrs['id'] \
            = "scraped-data-label-2"
        # ========================================================
        # PREPROCESSING 2: Fix URLs in the AZLyricsScraper section
        # ========================================================
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
        _, target_dd_tag_soup = find_dd_tag(id_=target_id, soup=azlyrics_soup)
        # Do the copying
        target_dd_tag_soup.replaceWith(copy_source_dd_tag_soup)
    return whole_soup


def post_process_api_reference(app, exception):
    """Process HTML files generated after the build process.

    This function is called when the `build-finished` event is emitted after the
    build has finished, before Sphinx exits [2]_.

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

    References
    ----------
    .. [2] `build-finished <https://bit.ly/2o3aynS>`_.

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
    # Find the <dt> tag that is a top sibling to the <dd> tag where we want to
    # add the <a> tag. We do that because the <dd> tag where we want to add the
    # update is not identified by an id.
    dt_tag = soup.find("dt", id="scrapers.azlyrics_scraper.AZLyricsScraper")
    dd_tag = dt_tag.find_next_sibling()
    # Replace the <code> tag with the new <a> tag
    dd_tag.p.code.replace_with(BeautifulSoup(new_tag, 'lxml').a)
    # ==============================
    # Save the modified HTML to disk
    # ==============================
    write_file(API_HTML_FILEPATH, str(soup))
