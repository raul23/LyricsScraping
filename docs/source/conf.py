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
exclude_patterns = ['scrapers.azlyrics*', 'scrapers.genius*', 'scrapers.lyrics*',
                    'scrapers.rst']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


def post_process(app, what, name, obj, options, lines):
    first_lines = ["Description", "-----------"]
    if name == "scrapers.scraper_exceptions":
        new_lines = first_lines + lines + ["Classes", "-------"]
        lines[:] = new_lines
    elif name == "scripts.scraper":
        new_lines = first_lines + lines + ["Functions", "---------"]
        lines[:] = new_lines
    elif what == 'module':
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
    app.connect('autodoc-process-docstring', post_process)
