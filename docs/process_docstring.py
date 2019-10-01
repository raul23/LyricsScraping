"""Module that ...

"""


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
    elif name in ["scripts.scraper", ""]:
        new_lines = first_lines + lines + ["Functions", "---------"]
        lines[:] = new_lines
    elif what == 'module':  # other modules
        last_lines = ["Class and methods", "-----------------"]
        new_lines = first_lines + lines + last_lines
        lines[:] = new_lines
    # Sphinx complaints that 'Functions' is an invalid section title
    """
    elif name == "scripts.scraper.edit_config":
        new_lines = ["Functions", "---------"] + lines
        lines[:] = new_lines
    """
