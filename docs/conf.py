# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys


# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
sys.path.insert(0, os.path.abspath('../'))
sys.path.insert(0, os.path.abspath('../lyrics_scraping'))

# Custom modules
from docs.postprocess import post_process_api_reference
from docs.process_docstring import add_custom_sections


# -- Project information -----------------------------------------------------

project = 'LyricsScraping'
copyright = '2019, Raul C.'
author = 'Raul C.'

# The full version, including alpha/beta/rc tags
release = '0.1'


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
    app.connect('build-finished', post_process_api_reference)
    # app.connect('source-read', source_read)
