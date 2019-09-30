# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import re
import sys
# Third-party modules
from bs4 import BeautifulSoup
sys.path.insert(0, os.path.abspath('../'))
sys.path.insert(0, os.path.abspath('../lyrics_scraping'))


# -- Project information -----------------------------------------------------

project = 'LyricsScraping'
copyright = '2019, Raul C.'
author = 'Raul C.'

# The full version, including alpha/beta/rc tags
release = '1.0.0'


# -- General configuration ---------------------------------------------------
master_doc = 'index'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    # 'm2r',
    # 'recommonmark',
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx_rtd_theme'
]
autodoc_mock_imports = ['pyutils', 'requests', 'yaml']
# This value controls the docstrings inheritance. Default is True.
# Ref.: https://bit.ly/2ofNvGi
# autodoc_inherit_docstrings = False
napoleon_google_docstring = False
# If False, no cross-referencing with Python types
napoleon_use_param = True
napoleon_use_ivar = True

source_suffix = '.rst'
# source_suffix = ['.rst', '.md']

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {'python': ('https://docs.python.org/3', None)}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    # 'scrapers.azlyrics*',
    'scrapers.genius*',
    # 'scrapers.lyrics*',
    'scrapers.rst'
]

# The default options for autodoc directives. They are applied to all autodoc
# directives automatically.
# Ref.: https://bit.ly/2mt4jsP
autodoc_default_options = {
    # 'private-members': True
    'inherited-members': True
}


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


# -- Register event handlers -------------------------------------------------

def add_custom_sections(app, what, name, obj, options, lines):
    """Add customized section titles to docstrings.

    The customized section titles must be added to a module's docstring.
    Otherwise, Sphinx will complaint that the title of the section is invalid.

    The description of the parameters is taken from sphinx's documentation [1]_.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        The Sphinx application object.
    what : str
         the type of the object which the docstring belongs to (one of
         "module", "class", "exception", "function", "method", "attribute").
    name
        the fully qualified name of the object.
    obj
        The object itself.
    options : dict
        The options given to the directive: an object with attributes
        `inherited_members`, `undoc_members`, `show_inheritance` and `noindex`
        that are true if the flag option of same name was given to the auto
        directive.
    lines : list of str
        The lines of the docstring. `lines` is a list of strings – the lines of
        the processed docstring – that the event handler can modify in place to
        change what Sphinx puts into the output.

    References
    ----------
    .. [1] `autodoc-process-docstring <https://bit.ly/2nghVI4>`_.

    """
    # TODO: find another way to add custom sections into docstrings
    first_lines = ["Description", "-----------"]
    if name == "scrapers.scraper_exceptions":
        new_lines = first_lines + lines + ["Classes", "-------"]
        lines[:] = new_lines
    elif name == "scripts.scraper":
        new_lines = first_lines + lines + ["Functions", "---------"]
        lines[:] = new_lines
    elif name == "scrapers.lyrics_scraper":
        last_lines = ["Class and methods", "-----------------"]
        new_lines = first_lines + lines + last_lines
        lines[:] = new_lines
    elif what == 'module':  # other modules
        last_lines = ["Classes and methods", "-------------------"]
        new_lines = first_lines + lines + last_lines
        lines[:] = new_lines
    # Complaints that Functions is an invalid section title
    """
    elif name == "scripts.scraper.edit_config":
        new_lines = ["Functions", "---------"] + lines
        lines[:] = new_lines
    """


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


def find_all_dl_tags(filepath):
    """

    Parameters
    ----------
    filepath : str

    Returns
    -------
    tuple : (bs4.BeautifulSoup, list)

    """
    html = read_file(filepath)
    soup = BeautifulSoup(html, 'lxml')
    return soup, soup.find_all("dl", class_="attribute")


def find_dd_tag(filepath, id):
    """

    Parameters
    ----------
    filepath : str
    id : str

    Returns
    -------
    list
    None

    """
    _, results = find_all_dl_tags(filepath)
    for res in results:
        if res.find(id=id):
            return res.find("dd")
    return None


def replace_dd_tag(filepath, source_id, target_id):
    """

    Parameters
    ----------
    filepath : str
    source_id : str
    target_id : str

    Returns
    -------
    soup : bs4.BeautifulSoup
    None

    """
    data = find_dd_tag(filepath, source_id)
    if data:
        soup, results = find_all_dl_tags(filepath)
        for res in results:
            if res.find(id=target_id):
                # TODO: explain
                data.find("p", id="scraped-data-label").attrs['id'] \
                    = "scraped-data-label-2"
                res.find("dd").replaceWith(data)
                return soup
    return None


def replace_hrefs(soup, replacements):
    """

    Parameters
    ----------
    soup : bs4.BeautifulSoup
    replacements : list of dict

    Returns
    -------
    soup : bs4.BeautifulSoup

    """

    def replace_href(pattern, replace_with):
        """

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


def post_process(app, exception):
    """

    Parameters
    ----------
    app
    exception

    """
    filepath = '_build/html/api_reference.html'
    whole_soup = replace_dd_tag(
        filepath=filepath,
        source_id="scrapers.lyrics_scraper.LyricsScraper.scraped_data",
        target_id="scrapers.azlyrics_scraper.AZLyricsScraper.scraped_data"
    )
    # TODO: explain '-2' in replace_with
    href_replacements = [
        {'pattern': re.compile("scraped-data-label$"),
         'replace_with': 'api_reference.html#scraped-data-label-2'
         },
        {'pattern': re.compile("lyrics_scraper.LyricsScraper.scraped_data$"),
         'replace_with': 'api_reference.html#scrapers.azlyrics_scraper.'
                         'AZLyricsScraper.scraped_data'
         }
    ]
    azlyrics_soup = whole_soup.find(id="module-scrapers.azlyrics_scraper",
                                    class_="section")
    replace_hrefs(azlyrics_soup, href_replacements)
    if whole_soup:
        write_file(filepath, str(whole_soup))


def setup(app):
    """Setup event handlers.

    This function is called at initialization time with one argument, the
    application object representing the Sphinx process [2].

    Parameters
    ----------
    app : sphinx.application.Sphinx
        The Sphinx application object.

    Notes
    -----
    More information about events at `Sphinx core events`_.

    References
    ----------
    .. [2] `setup function <https://bit.ly/2ng7qEM>`_.

    .. _Sphinx core events: https://bit.ly/2lNISTe

    """
    # Connect (register) handlers to events
    app.connect('autodoc-process-docstring', add_custom_sections)
    app.connect('build-finished', post_process)
    # app.connect('source-read', source_read)
