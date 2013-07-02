Meze
====

Meze adds `Sphinx`_ flavor to `Mezzanine`_.

.. _Sphinx: http://sphinx-doc.org/
.. _Mezzanine: http://mezzanine.jupo.org/

Quick start
-----------

1. Add "meze" to your ``INSTALLED_APPS`` setting like this::

   INSTALLED_APPS = (
       ...
       'meze',
   )

2. Inject ``source`` and ``convert`` fields to
   ``mezzanine.blog.models.BlogPost`` and
   ``mezzanine.pages.models.RichTextPage.source`` models as follows::

   help_text = ("Source in reStructuredText format will be converted to "
                  "HTML and result will replace content field.  Uncheck ")
   EXTRA_MODEL_FIELDS = (
       ("mezzanine.blog.models.BlogPost.source",
        "TextField", (), {"blank": True, "help_text": help_text}),
       ("mezzanine.blog.models.BlogPost.convert",
        "BooleanField", ("Convert source",), {"default": True}),

       ("mezzanine.pages.models.RichTextPage.source",
        "TextField", (), {"blank": True, "help_text": help_text}),
       ("mezzanine.pages.models.RichTextPage.convert",
        "BooleanField", ("Convert source",), {"default": True}),
   )
   del help_text