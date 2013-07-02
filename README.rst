Meze
====

Quick start
-----------

1. Add "meze" to your ``INSTALLED_APPS`` setting like this::

   INSTALLED_APPS = (
       ...
       'meze',
   )

2. Inject `source` to ``mezzanine.blog.models.BlogPost`` and
   ``mezzanine.pages.models.RichTextPage.source`` models as follows::

    EXTRA_MODEL_FIELDS = (
        ("mezzanine.blog.models.BlogPost.source",
         "TextField", ("reStructuredText",), {"blank": True}),
        ("mezzanine.pages.models.RichTextPage.source",
         "TextField", ("reStructuredText",), {"blank": True}),
    )