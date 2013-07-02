import os
import time
from django.conf import settings
from django.contrib import messages


SETTINGS = settings.MEZE_SETTINGS
BUILDER = SETTINGS.get('builder', 'sphinx').lower()
REMOVE = SETTINGS.get('remove', 'all')

SPHINX_ROOT = WORKDIR = SETTINGS.get('workdir', settings.PROJECT_ROOT)
SPHINX_BUILD = os.path.join(SPHINX_ROOT, '_build')
SPHINX_TEMPLATES = os.path.join(SPHINX_ROOT, 'templates')

SPHINX_INDEX = """
.. toctree::
   :glob:

   *
   */*
   */*/*
   */*/*/*
"""
SPHINX_LAYOUT = "{% block body %}{% endblock %}"
SPHINX_CONF = """# -*- coding: utf-8 -*-
# A simple Sphinx configuration

# following are not needed
project = u''
copyright = u''
version = release = '0'

master_doc = 'index'


exclude_patterns = ['_build', 'templates']
#html_static_path = ['static']
templates_path = ['templates']

pygments_style = 'sphinx'
html_theme = 'default'
html_sidebars = {'**': []}
html_domain_indices = False
html_use_index = False
html_show_sourcelink = False


source_suffix = '.rst'
extensions = ['sphinx.ext.intersphinx']

intersphinx_mapping = {
    'python': ('http://docs.python.org/', None),
}

extlinks = {
    'wiki': ('http://en.wikipedia.org/wiki/%s', ''),
}
"""


def sphinx_setup():

    for folder in [SPHINX_ROOT, SPHINX_BUILD, SPHINX_TEMPLATES]:
        if not os.path.isdir(folder):
            os.makedirs(folder)

    layout = os.path.join(SPHINX_TEMPLATES, 'layout.html')
    if not os.path.isfile(layout):
        with open(layout, 'w') as out:
            out.write(SPHINX_LAYOUT)

    conf = os.path.join(SPHINX_ROOT, 'conf.py')
    if not os.path.isfile(conf):
        with open(conf, 'w') as out:
            out.write(SPHINX_CONF)


def sphinx_build(source, slug='index', old_slug=None):

    from sphinx import main
    meze_messages = []
    if slug != 'index':
        rst = os.path.join(SPHINX_ROOT, 'index.rst')
        with open(rst, 'w') as out:
            out.write(SPHINX_INDEX)

    folder, filename = os.path.split(os.path.join(SPHINX_ROOT, slug))
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)

    if old_slug:
        for fname in [os.path.join(SPHINX_ROOT, old_slug + '.rst'),
                      os.path.join(SPHINX_BUILD, old_slug + '.html')]:
            if os.path.isfile(fname):
                os.remove(fname)

    rst = os.path.join(folder, filename + '.rst')
    with open(rst, 'w') as inp:
        inp.write(source)

    cwd = os.getcwd()
    os.chdir(SPHINX_ROOT)
    start = time.time()
    main(['sphinx-build', SPHINX_ROOT, SPHINX_BUILD, rst])
    meze_messages.append((messages.INFO,
                          'Source was converted into HTML using Sphinx in '
                          '{:.2f}'.format(time.time() - start)))
    os.chdir(cwd)

    html = os.path.join(SPHINX_BUILD, slug + '.html')
    with open(html) as inp:
        content = inp.read().strip()
    return content, meze_messages


def rst2html(rst, slug=None, old_slug=None):

    if BUILDER == 'sphinx':
        sphinx_setup()
        builder = sphinx_build
    else:
        raise ValueError('unknown builder: ' + BUILDER)

    return builder(rst, slug, old_slug)
