import re
import os
import sys
import time
import codecs

from django.conf import settings
from django.contrib import messages

from sphinx import builders
from sphinx.application import Sphinx
from sphinx.util.console import nocolor
from sphinx.builders.html import SerializingHTMLBuilder
from sphinx.util.osutil import ensuredir, os_path

nocolor()

try:
    SETTINGS = settings.MEZE_SETTINGS
except AttributeError:
    SETTINGS = {}

WORKDIR = SETTINGS.get('workdir', settings.PROJECT_ROOT)
IMGEXTS = set(['.gif', '.png', '.jpg'])

try:
    SPHINX_CONF = settings.SPHINX_CONF
except AttributeError:
    SPHINX_CONF = """project = copyright = u''
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
intersphinx_mapping = {'python': ('http://docs.python.org/', None)}
extlinks = {'wiki': ('http://en.wikipedia.org/wiki/%s', ''),}
extensions = ['sphinx.ext.intersphinx', 'sphinx.ext.extlinks']"""

SPHINX_CONF_APPEND = """

try:
    rst_prolog += ''
except NameError:
    rst_prolog = ''

rst_prolog += '''
.. role:: strike
   :class: strike
'''
"""

# all needs to return True to keep a message
MESSAGE_FILTERS = [
    #lambda msg: 'nonlocal image URI found' not in msg
]


def find_images():
    """Return a dictionary of images in static and media root folders.
    Dictionary maps image file names to full paths."""

    images = {}
    static_root = settings.STATIC_ROOT
    media_root = settings.MEDIA_ROOT
    if static_root.startswith(media_root):
        roots = [media_root]
    elif media_root.startswith(static_root):
        roots = [static_root]
    else:
        roots = [static_root, media_root]

    for aroot in roots:
        for root, dirs, files in os.walk(aroot):
            for fn in files:
                if os.path.splitext(fn)[1].lower() in IMGEXTS:
                    path = os.path.join(
                        settings.STATIC_URL.strip('/'),
                        root[len(static_root):].strip('/'),
                        fn)
                    items = path.split('/')
                    for i in range(len(items)):
                        key = '/'.join(items[i:])
                        if key in images:
                            break
                        else:
                            images[key] = path
    return images


class MezeBuilder(SerializingHTMLBuilder):
    """A serialized builder to help minimize Sphinx output."""

    implementation = None
    implementation_dumps_unicode = True
    name = 'meze'
    out_suffix = ''
    copysource = False
    context = None

    def init(self):

        SerializingHTMLBuilder.init(self)

    def dump_context(self, context, filename):
        """Hold context as a class variable."""

        MezeBuilder.context = context

    def handle_page(self, pagename, ctx, templatename='page.html',
                    outfilename=None, event_arg=None):
        """Serializing builder copies source files even when configuration
        setting *html_copy_source* is **False**.  This overwrites that
        function to avoid making a copy of the source."""

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

        try:
            self.stream.flush()
        except IOError:
            pass


class Meze(object):

    def __init__(self, source, workdir=WORKDIR):

        self._source = source
        self._workdir = workdir
        self._messages = []
        self._content = None

    def sphinx_build(self):

        workdir = self._workdir
        if not os.path.isdir(workdir):
            os.makedirs(workdir)

        conf = os.path.join(workdir, 'conf.py')
        with codecs.open(conf, encoding='utf-8', mode='w') as out:
            out.write(SPHINX_CONF)
            out.write(SPHINX_CONF_APPEND)

        start = time.time()
        status = MezeStream(sys.stdout)
        warning = MezeStream(sys.stderr)
        app = Sphinx(srcdir=workdir, confdir=workdir, outdir=workdir,
                     doctreedir=workdir, buildername='meze',
                     confoverrides={}, status=status, warning=warning,
                     freshenv=False, warningiserror=False, tags=[])

        rst = os.path.join(workdir, 'index' + app.config.source_suffix)
        with codecs.open(rst, encoding='utf-8', mode='w') as out:
            out.write(self._source)

        app.build(False, [rst])

        self._messages.append((messages.INFO, 'Source was converted '
                               'into HTML using Sphinx in {:.2f}'.
                               format(time.time() - start)))
        for msg in warning.messages:
            items = msg.split('WARNING: ')
            if len(items) == 2:
                msg = items[1]
            self._messages.append((messages.WARNING, msg))

        self._content, MezeBuilder.context = MezeBuilder.context['body'], None

    def revise_images(self):

        images = find_images()

        content = self._content
        unique = set(re.findall('src="(.*?)"', content))
        for src in unique:
            # suppress image related Sphinx messages

            if not src.startswith('http'):
                path = None
                if src in images:
                    path = images[src]
                else:
                    items = src.split('/')
                    for i in range(1, len(items)):
                        new = '/'.join(items[i:])
                        if new in images:
                            path = images[new]
                            break
                    else:
                        self._messages.append((messages.WARNING,
                                               'Image file "{}" was not found.'
                                               .format(src)))
                if src != path:
                    self._messages.append((messages.INFO, 'Image source "{}" '
                                           'was substituted with "{}".'
                                           .format(src, path)))
                if path:
                    content = content.replace('="' + src + '"',
                                              '="/' + path + '"')
                    self._messages = [msg for msg in self._messages
                                      if src not in msg[1]]
        self._content = content

    def revise_headers(self):

        content = re.sub('<h5>(.*)</h5>', '<h6>\\1</h6>', self._content)
        content = re.sub('<h4>(.*)</h4>', '<h5>\\1</h5>', content)
        content = re.sub('<h3>(.*)</h3>', '<h4>\\1</h4>', content)
        content = re.sub('<h2>(.*)</h2>', '<h3>\\1</h3>', content)
        self._content = re.sub('<h1>(.*)</h1>', '<h2>\\1</h2>', content)

    def filter_messages(self):
        """Remove uninformative warning messages from Sphinx."""

        self._messages = [(lvl, msg) for lvl, msg in self._messages
                          if all([fltr(msg) for fltr in MESSAGE_FILTERS])]


def rst2html(rst):

    meze = Meze(rst)
    meze.sphinx_build()
    meze.revise_headers()
    meze.revise_images()
    meze.filter_messages()
    return meze._content, meze._messages
