from copy import deepcopy
from django import forms
from django.contrib import admin, messages
from mezzanine.blog.admin import BlogPostAdmin
from mezzanine.blog.models import BlogPost
from mezzanine.pages.admin import PageAdmin
from mezzanine.pages.models import RichTextPage

from .meze import rst2html

blog_fieldsets = deepcopy(BlogPostAdmin.fieldsets)
blog_fieldsets[0][1]["fields"].insert(-2, "source")
blog_fieldsets[0][1]["fields"].insert(-2, "convert")

ADMIN_CSS = {'all': ('css/meze_admin.css', 'css/pygments.css')}

def add_meze_messages(request, form):
    """Add *meze_messages* in *form* data to the *request* object."""

    for level, message in form.data.get('meze_messages', []):
        if level == messages.WARNING:
            message = 'Meze (WARNING): ' + message
        else:
            message = 'Meze: ' + message
        messages.add_message(request, level, message)


class MezeForm(forms.ModelForm):

    root = ""

    def __init__(self, *args, **kwargs):

        if args:
            data = args[0]
            if 'convert' in data and data['convert']:
                try:
                    source = data['source']
                except KeyError:
                    pass
                else:
                    old_source = None
                    if 'instance' in kwargs:
                        obj = kwargs['instance']
                        old_source = obj.source

                    if source != old_source:
                        (data['content'],
                         data['meze_messages']) = rst2html(source)

        super(MezeForm, self).__init__(*args, **kwargs)


class BlogPostForm(MezeForm):

    root = "blog"

    class Meta:

        model = BlogPost


class BlogPostAdmin_(BlogPostAdmin):

    form = BlogPostForm

    class Media:

        css = ADMIN_CSS
    fieldsets = blog_fieldsets

    def save_model(self, request, obj, form, change):

        add_meze_messages(request, form)
        super(BlogPostAdmin_, self).save_model(request, obj, form, change)


admin.site.unregister(BlogPost)
admin.site.register(BlogPost, BlogPostAdmin_)


class RichTextForm(MezeForm):

    root = ""

    class Meta:

        model = RichTextPage


class RichTextAdmin(PageAdmin):

    form = RichTextForm

    class Media:

        css = ADMIN_CSS

    def save_model(self, request, obj, form, change):

        add_meze_messages(request, form)
        super(RichTextAdmin, self).save_model(request, obj, form, change)


admin.site.unregister(RichTextPage)
admin.site.register(RichTextPage, RichTextAdmin)
