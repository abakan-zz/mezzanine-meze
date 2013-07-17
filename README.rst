Meze
====

Meze adds `Sphinx`_ flavor to `Mezzanine`_. You can write your blog posts and
pages in `reStructuredText`_ and get them converted into HTML via Sphinx.

Usage Examples
--------------

See a number of usage examples at: http://ahmetbakan.com/blog/category/meze/

Requirements
------------

`Sphinx`_ is required to convert reStructuredText source.

Installation
------------

You can use ``easy_install`` or ``pip``:

::

   easy_install -U mezzanine-meze
   pip install mezzanine-meze

or download package from https://pypi.python.org/pypi/mezzanine-meze
and install using ``setup.py``.


Quick start
-----------

Make the following changes in your project ``settings.py`` file:

1. Add "meze" to ``INSTALLED_APPS``::

     INSTALLED_APPS = (
         ...
         'meze',
     )

2. Inject ``source`` and ``convert`` fields to
   ``mezzanine.blog.models.BlogPost`` and
   ``mezzanine.pages.models.RichTextPage.source`` models::

     help_text = ("Source in reStructuredText format will be converted to "
                  "HTML and result will replace content field.")
     EXTRA_MODEL_FIELDS = (
         # Enable Meze for blog posts
         ("mezzanine.blog.models.BlogPost.source",
          "TextField", (), {"blank": True, "help_text": help_text}),
         ("mezzanine.blog.models.BlogPost.convert",
          "BooleanField", ("Convert source",), {"default": True}),
         # Enable Meze for rich text pages
         ("mezzanine.pages.models.RichTextPage.source",
          "TextField", (), {"blank": True, "help_text": help_text}),
         ("mezzanine.pages.models.RichTextPage.convert",
          "BooleanField", ("Convert source",), {"default": True}),
     )
     del help_text

   If you have started using Meze after creating database, you may need to
   make a migration. See field injection `caveats`_ in Mezzanine documentation.

   .. _caveats: http://mezzanine.jupo.org/docs/model-customization.html#field-injection-caveats


3. Update ``settings.py`` file.

   Add ``MEZE_SETTINGS``::

     MEZE_SETTINGS = {
         'workdir': os.path.join(PROJECT_ROOT, 'meze_workdir'),
     }

   Default values are shown. You will need write access to ``workdir``.

   Add `configuration`_  options for Sphinx::

     SPHINX_CONF = """
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

   This file is written to Meze ``workdir``.

   .. _configuration: http://sphinx-doc.org/config.html


4. Sphinx is using `Pygments`_ for syntax highlighting, so you will need to
   add ``pygments.css`` file to your template::

      {% compress css %}
      ...
      <link rel="stylesheet" href="{% static "css/pygments.css" %}">
      ...

   For Python code, you can also add ``copybutton.js`` file, which will
   help displaying code in a copy friendly format::

      {% compress js %}
      ...
      <script src="{% static "js/copybutton.js" %}"></script>
      ...

   .. _Pygments: http://pygments.org/


How does it work?
-----------------

Meze starts a `Sphinx`_ project in ``workdir`` by creating a simple
configuration file (``conf.py``).


reStructuredText files are written into ``workdir``, HTML files are built
using Sphinx, and content of HTML files are stored in the database.


Source code
-----------

https://github.com/abakan/mezzanine-meze


.. _Sphinx: http://sphinx-doc.org/
.. _Mezzanine: http://mezzanine.jupo.org/
.. _reStructuredText: http://docutils.sourceforge.net/rst.html
.. _caveats: http://mezzanine.jupo.org/docs/model-customization.html#field-injection-caveats
.. _configuration: http://sphinx-doc.org/config.html


Changes
-------

v0.2.1 (July 17, 2013)
^^^^^^^^^^^^^^^^^^^^^^

  * Fixed a bug in `Meze` class that prevented changes in Sphinx configuration
    to take place.

v0.2 (July 12, 2013)
^^^^^^^^^^^^^^^^^^^^

  * Improved handling of image files.

v0.1 (July 11, 2013)
^^^^^^^^^^^^^^^^^^^^


  * First release.