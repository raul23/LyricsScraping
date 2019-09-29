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
import sys
import sphinx_rtd_theme
sys.path.insert(0, os.path.abspath('../../'))
sys.path.insert(0, os.path.abspath('../../lyrics_scraping'))


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
autodoc_mock_imports = ['bs4', 'pyutils', 'requests', 'yaml']
napoleon_google_docstring = False
# If False, no cross-referencing with Python types
napoleon_use_param = True
napoleon_use_ivar = True

source_suffix = '.rst'
# source_suffix = ['.rst', '.md']

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {'python': ('http://docs.python.org/3', None)}

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    'scrapers.azlyrics*',
    'scrapers.genius*',
    # 'scrapers.lyrics*',
    'scrapers.rst'
]

# The default options for autodoc directives. They are applied to all autodoc
# directives automatically.
# Ref.: https://bit.ly/2mt4jsP
autodoc_default_options = {
    # 'private-members': True
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
