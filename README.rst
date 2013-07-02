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

Quick start
-----------


1. Add "meze" to your ``INSTALLED_APPS`` setting like this::

     INSTALLED_APPS = (
         ...
         'meze',
     )

2. Edit your project :file:`settings.py` file to inject ``source`` and
   ``convert`` fields to ``mezzanine.blog.models.BlogPost`` and
   ``mezzanine.pages.models.RichTextPage.source`` models as follows::

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

3. Add ``MEZE_SETTINGS`` to :file:`settings.py`::

     MEZE_SETTINGS = {
      'workdir': os.path.join(PROJECT_ROOT, 'meze_workdir'),
      'builder': 'sphinx',
     }

   Default values are shown. You will need write access to :file:`workdir`.



.. _caveats: http://mezzanine.jupo.org/docs/model-customization.html#field-injection-caveats