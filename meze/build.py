import re
import os
import time
from django.conf import settings
from django.contrib import messages


SETTINGS = settings.MEZE_SETTINGS
BUILDER = SETTINGS.get('builder', 'sphinx').lower()

HEADER2 = SETTINGS.get('header2', True)

SPHINX_ROOT = SETTINGS.get('workdir', settings.PROJECT_ROOT)
SPHINX_CONF = """# -*- coding: utf-8 -*-
# A simple Sphinx configuration

# following are not needed
project = u''
copyright = u''
version = release = '0'

master_doc = 'index'

pygments_style = 'sphinx'
html_theme = 'default'
html_sidebars = {'**': []}
html_domain_indices = False
html_use_index = False
html_show_sourcelink = False
html_add_permalinks = None

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
    """Make working directory and write configuration file."""

    for folder in [SPHINX_ROOT]:
        if not os.path.isdir(folder):
            os.makedirs(folder)

    conf = os.path.join(SPHINX_ROOT, 'conf.py')
    if not os.path.isfile(conf):
        with open(conf, 'w') as out:
            out.write(SPHINX_CONF)


import sys
import codecs
from sphinx import builders
from sphinx.application import Sphinx
from sphinx.util.console import nocolor
from sphinx.builders.html import SerializingHTMLBuilder

nocolor()


class MezeBuilder(SerializingHTMLBuilder):

    implementation = None
    implementation_dumps_unicode = True
    name = 'meze'
    out_suffix = ''

    context = None

    def init(self):

        SerializingHTMLBuilder.init(self)

    def dump_context(self, context, filename):
        """Save context as class variable."""

        MezeBuilder.context = context

    def finish(self):
        """Do not write object inventory and search index."""

        pass

# Sphinx.add_builder needs to be called after instantiation
# but builder is initialized during instantiation
# adding MezeBuilder to built-in builders
builders.BUILTIN_BUILDERS['meze'] = MezeBuilder


class MezeStream(object):

    """Hold messages written to a stream."""

    def __init__(self, stream):

        self.stream = stream
        self.messages = []

    def write(self, str):

        self.stream.write(str)
        self.messages.append(str)

    def flush(self, *args, **kwargs):

        self.stream.flush()


def sphinx_build(source, slug='index', old_slug=None):
    """Write source into `index.rst` and build using Sphinx."""

    meze_messages = []
    rst = os.path.join(SPHINX_ROOT, 'index.rst')
    with codecs.open(rst, encoding='utf-8', mode='w') as inp:
        inp.write(source)
    start = time.time()

    status = MezeStream(sys.stdout)
    warning = MezeStream(sys.stderr)

    Sphinx(srcdir=SPHINX_ROOT, confdir=SPHINX_ROOT, outdir=SPHINX_ROOT,
           doctreedir=os.path.join(SPHINX_ROOT, '.doctrees'),
           buildername='meze', confoverrides={},
           status=status, warning=warning, freshenv=False,
           warningiserror=False, tags=[]).build(False, [rst])
    meze_messages.append((messages.INFO,
                          'Source was converted into HTML using Sphinx in '
                          '{:.2f}'.format(time.time() - start)))
    for msg in warning.messages:
        meze_messages.append((messages.WARNING, msg))
    content = MezeBuilder.context['body']
    return content, meze_messages


def rst2html(rst, slug=None, old_slug=None):

    if BUILDER == 'sphinx':
        sphinx_setup()
        builder = sphinx_build
    else:
        raise ValueError('unknown builder: ' + BUILDER)

    content, meze_messages = builder(rst, slug, old_slug)
    if HEADER2:
        content = re.sub('<h5>(.*)</h5>', '<h6>\\1</h6>', content)
        content = re.sub('<h4>(.*)</h4>', '<h5>\\1</h5>', content)
        content = re.sub('<h3>(.*)</h3>', '<h4>\\1</h4>', content)
        content = re.sub('<h2>(.*)</h2>', '<h3>\\1</h3>', content)
        content = re.sub('<h1>(.*)</h1>', '<h2>\\1</h2>', content)
    return content, meze_messages
