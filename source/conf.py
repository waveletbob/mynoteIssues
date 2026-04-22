# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = '个人技术笔记'
copyright = '2023, waveletbob'
author = 'waveletbob'
release = '1.0.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

language = 'zh_CN'

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'myst_parser',  # Markdown support
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.mathjax',
    'sphinx.ext.intersphinx',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinxcontrib.disqus',
    'sphinx_design',  # Modern design components
    'sphinx_copybutton',  # Copy button for code blocks
]

# MyST Parser configuration
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]

myst_enable_checkboxes = True
myst_heading_anchors = 3  # Add anchors to headings up to level 3

# Source file configuration
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# The master toctree document
master_doc = 'index'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
templates_path = ['_templates']

# Theme options
html_theme_options = {
    'navigation_depth': 4,
    'collapse_navigation': False,
    'sticky_navigation': True,
    'includehidden': True,
    'titles_only': False
}

# HTML context for GitHub integration
html_context = {
    'display_github': True,
    'github_user': 'waveletbob',
    'github_repo': 'mynoteIssues',
    'github_version': 'main',
    'conf_py_path': '/source/',
}

# Add any paths that contain custom static files
html_static_path = ['_static', 'images']

# The encoding of source files
source_encoding = 'utf-8'

# Pygments style
pygments_style = 'sphinx'

# If true, `todo` and `todoList` produce output
todo_include_todos = True

# -- Options for LaTeX output ---------------------------------------------

latex_elements = {
    # The paper size ('letterpaper' or 'a4paper').
    'papersize': 'a4paper',
}

# Grouping the document tree into LaTeX files
latex_documents = [
    (master_doc, 'notes.tex', '个人技术笔记',
     author, 'manual'),
]

# -- Options for manual page output ---------------------------------------

man_pages = [
    (master_doc, 'notes', '个人技术笔记',
     [author], 1)
]

# -- Options for Texinfo output -------------------------------------------

texinfo_documents = [
    (master_doc, 'notes', '个人技术笔记',
     author, 'notes', '个人技术知识库',
     'Miscellaneous'),
]
