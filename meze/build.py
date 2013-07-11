import re
import os
import sys
import time
import codecs
import StringIO

from django.conf import settings
from django.contrib import messages

from docutils.io import Input, FileInput

from sphinx import builders
from sphinx import environment
from sphinx.application import Sphinx
from sphinx.util.console import nocolor
from sphinx.builders.html import SerializingHTMLBuilder
from sphinx.util.osutil import ensuredir, os_path

nocolor()

try:
    SETTINGS = settings.MEZE_SETTINGS
except AttributeError:
    SETTINGS = {}

WORKDIR = SETTINGS.get('workdir', os.path.join(settings.PROJECT_ROOT,
                                               'meze_workdir'))


SPHINX_CONF = settings.SPHINX_CONF or """
project = u''
copyright = u''
version = '0'
release = '0'
master_doc = 'index'
pygments_style = 'sphinx'
html_theme = 'default'
html_sidebars = {'**': []}
html_domain_indices = False
html_use_index = False
html_show_sourcelink = False
html_add_permalinks = None
source_suffix = '.rst'
intersphinx_mapping = {'python': ('http://docs.python.org/', None)}
extlinks = {'wiki': ('http://en.wikipedia.org/wiki/%s', ''),}
extensions = ['sphinx.ext.intersphinx', 'sphinx.ext.extlinks']
"""


def sphinx_setup():
    """Make working directory and write configuration file."""

    if not os.path.isdir(WORKDIR):
        os.makedirs(WORKDIR)


class MezeBuilder(SerializingHTMLBuilder):

    implementation = None
    implementation_dumps_unicode = True
    name = 'meze'
    out_suffix = ''
    copysource = False
    context = None

    def init(self):

        SerializingHTMLBuilder.init(self)

    def dump_context(self, context, filename):
        """Save context as class variable."""

        MezeBuilder.context = context

    def handle_page(self, pagename, ctx, templatename='page.html',
                    outfilename=None, event_arg=None):
        """Do not copy sources."""

        ctx['current_page_name'] = pagename
        self.add_sidebars(pagename, ctx)

        if not outfilename:
            outfilename = os.path.join(self.outdir,
                                       os_path(pagename) + self.out_suffix)

        self.app.emit('html-page-context', pagename, templatename,
                      ctx, event_arg)

        ensuredir(os.path.dirname(outfilename))
        self.dump_context(ctx, outfilename)

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


def sphinx_build(source, slug='index'):
    """Write source file and build using Sphinx."""

    meze_messages = []
    start = time.time()
    status = MezeStream(sys.stdout)
    warning = MezeStream(sys.stderr)

    def get_matching_docs(dirname, suffix, exclude_matchers=(),
                          found_docs=set([slug])):
        """Match only slug."""

        return found_docs

    class FakeFileInput(FileInput):

        def __init__(self, source=StringIO.StringIO(source), source_path=None,
                     encoding=None, error_handler='strict',
                     autoclose=True, handle_io_errors=True, mode='rU'):
            FileInput.__init__(self, source=source, source_path=None,
                               encoding=None, error_handler='strict',
                               autoclose=True, handle_io_errors=True,
                               mode='rU')

    #environment.get_matching_docs = get_matching_docs
    #environment.FileInput = FakeFileInput

    app = Sphinx(srcdir=WORKDIR, confdir=WORKDIR, outdir=WORKDIR,
                 doctreedir=WORKDIR, buildername='meze',
                 confoverrides={}, status=status, warning=warning,
                 freshenv=False, warningiserror=False, tags=[])

    rst = os.path.join(WORKDIR, 'index' + app.config.source_suffix)
    with codecs.open(rst, encoding='utf-8', mode='w') as out:
        out.write(source)

    conf = os.path.join(WORKDIR, 'conf.py')
    with codecs.open(conf, encoding='utf-8', mode='w') as out:
        out.write(SPHINX_CONF)

    app.build(False, [rst])

    meze_messages.append((messages.INFO,
                          'Source was converted into HTML using Sphinx in '
                          '{:.2f}'.format(time.time() - start)))
    for msg in warning.messages:
        meze_messages.append((messages.WARNING, msg))

    content = MezeBuilder.context['body']

    return content, meze_messages


def rst2html(rst, slug=None):

    sphinx_setup()
    content, meze_messages = sphinx_build(rst, slug)

    # downgrade headers
    content = re.sub('<h5>(.*)</h5>', '<h6>\\1</h6>', content)
    content = re.sub('<h4>(.*)</h4>', '<h5>\\1</h5>', content)
    content = re.sub('<h3>(.*)</h3>', '<h4>\\1</h4>', content)
    content = re.sub('<h2>(.*)</h2>', '<h3>\\1</h3>', content)
    content = re.sub('<h1>(.*)</h1>', '<h2>\\1</h2>', content)
    # correct image source
    content = re.sub('src=\"(.*)\"', 'src=\"/\\1\"', content)
    content = re.sub('src=\"/(http[s]?:.*)\"', 'src=\"\\1\"', content)

    return content, meze_messages
