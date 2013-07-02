import os
import time
from copy import deepcopy
from django import forms
from django.contrib import admin, messages
from mezzanine.blog.admin import BlogPostAdmin
from mezzanine.blog.models import BlogPost
from mezzanine.pages.admin import PageAdmin
from mezzanine.pages.models import RichTextPage

from .build import rst2html

blog_fieldsets = deepcopy(BlogPostAdmin.fieldsets)
blog_fieldsets[0][1]["fields"].insert(-2, ("source", "convert"))


class BlogPostForm(forms.ModelForm):

    class Meta:
        model = BlogPost

    def __init__(self, *args, **kwargs):

        if args:
            data = args[0]
            try:
                source = data['source']
            except KeyError:
                pass
            else:
                old_source = old_slug = None
                if 'instance' in kwargs:
                    obj = kwargs['instance']
                    old_source = obj.source
                    old_slug = obj.slug

                if source != old_source:
                    slug = data['slug']
                    if slug != old_slug:
                        old_slug = None
                    else:
                        old_slug = os.path.join('blog', slug)
                    slug = os.path.join('blog', slug)

                    (data['content'],
                     data['meze_messages']) = rst2html(source, slug, old_slug)

        super(BlogPostForm, self).__init__(*args, **kwargs)


class BlogPostAdmin_(BlogPostAdmin):

    form = BlogPostForm

    class Media:

        css = {'all': ('css/meze_admin.css', 'css/pygments.css')}

    fieldsets = blog_fieldsets

    def save_model(self, request, obj, form, change):

        for level, message in form.data.get('meze_messages', []):
            messages.add_message(request, level, message)

        super(BlogPostAdmin_, self).save_model(request, obj, form, change)


admin.site.unregister(BlogPost)
admin.site.register(BlogPost, BlogPostAdmin_)


class RichTextAdmin(PageAdmin):

    class Media:

        css = {'all': ('meze_admin.css', 'pygments.css')}

    def save_model(self, request, obj, form, change):

        super(RichTextAdmin, self).save_model(request, obj, form, change)
        if obj.source:
            obj.content = rst2html(obj.source, obj.slug)
        obj.save()

admin.site.unregister(RichTextPage)
admin.site.register(RichTextPage, RichTextAdmin)
