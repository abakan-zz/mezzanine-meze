Meze
====

Meze adds `Sphinx`_ flavor to `Mezzanine`_. You can write your blog posts and
pages in `reStructuredText`_ and get them converted into HTML using Sphinx.

.. _Sphinx: http://sphinx-doc.org/
.. _Mezzanine: http://mezzanine.jupo.org/
.. _reStructuredText: http://docutils.sourceforge.net/rst.html

Requirements
------------

`Sphinx`_ is required to convert reStructuredText source.

Installation
------------

If you have easy_install available on your system, just type:

::

   easy_install -U Meze

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

3. Add ``MEZE_SETTINGS``::

     MEZE_SETTINGS = {
      'workdir': os.path.join(PROJECT_ROOT, 'meze_workdir'),
      'builder': 'sphinx',
     }

   Default values are shown. You will need write access to ``workdir``.
   Sphinx is currently the only builder.


4. If you have started using Meze after creating database, you may need to
   make a migration. See field injection `caveats`_ in Mezzanine documentation.

.. _caveats: http://mezzanine.jupo.org/docs/model-customization.html#field-injection-caveats


How does it work?
-----------------

Meze starts a `Sphinx`_ project in :``workdir`` by creating a simple
configuration file (``conf.py``) and an HTML template
(``templates/layout.html``). `Configuration` file can be customized to
add more Sphinx extensions.

.. _Configuration: http://sphinx-doc.org/config.html

reStructuredText files are written into ``workdir``, HTML files are built
using Sphinx, and content of HTML files are stored in the database.


