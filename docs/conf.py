from pallets_sphinx_themes import get_version
from pallets_sphinx_themes import ProjectLink

# Project --------------------------------------------------------------

project = "Flask-WTF"
copyright = "2010 WTForms"
author = "WTForms"
release, version = get_version("Flask-WTF")

# General --------------------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinxcontrib.log_cabinet",
    "pallets_sphinx_themes",
    "sphinx_issues",
]
autodoc_typehints = "description"
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "flask": ("https://flask.palletsprojects.com/", None),
    "wtforms": ("https://wtforms.readthedocs.io/", None),
}
issues_github_path = "pallets-eco/flask-wtf"

# HTML -----------------------------------------------------------------

html_theme = "flask"
html_theme_options = {"index_sidebar_logo": False}
html_context = {
    "project_links": [
        ProjectLink("PyPI Releases", "https://pypi.org/project/Flask-WTF/"),
        ProjectLink("Source Code", "https://github.com/pallets-eco/flask-wtf/"),
        ProjectLink(
            "Issue Tracker", "https://github.com/pallets-eco/flask-wtf/issues/"
        ),
        ProjectLink("Chat", "https://discord.gg/pallets"),
    ]
}
html_sidebars = {
    "index": ["project.html", "localtoc.html", "searchbox.html", "ethicalads.html"],
    "**": ["localtoc.html", "relations.html", "searchbox.html", "ethicalads.html"],
}
singlehtml_sidebars = {"index": ["project.html", "localtoc.html", "ethicalads.html"]}
html_static_path = ["_static"]
html_favicon = "_static/flask-wtf-icon.png"
html_logo = "_static/flask-wtf-icon.png"
html_title = f"{project} Documentation ({version})"
html_show_sourcelink = False
