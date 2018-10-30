#!/usr/bin/env python
# coding: utf-8
import django

if django.VERSION >= (1, 10) and django.VERSION < (2, 1):
    from django.urls import reverse
elif django.VERSION >= (2, 1):
    from django.urls import reverse_lazy as reverse
else:
    from django.core.urlresolvers import reverse

from django.utils.safestring import mark_safe
from django.utils.html import escape
from django.template import Template, Context

from table.utils import Accessor
from table.columns.base import Column


class LinkColumn(Column):
    def __init__(self, header=None, links=None, delimiter='&nbsp', default=None, field=None, **kwargs):
        self.links = links
        self.delimiter = delimiter
        kwargs['safe'] = False
        kwargs["searchable"] = False
        super(LinkColumn, self).__init__(field, header, default=default, **kwargs)

    def render(self, obj):
        text = self.delimiter.join([link.render(obj) for link in self.links])
        return text if text else self.default


class Link(object):
    """
    Represents a html <a> tag.
    """
    def __init__(self, text=None, viewname=None, args=None, kwargs=None, urlconf=None, current_app=None, attrs=None,
                 cond_disable=None):
        self.basetext = text
        self.viewname = viewname
        self.args = args or []
        self.kwargs = kwargs or {}
        self.urlconf = urlconf
        self.current_app = current_app
        self.base_attrs = attrs or {}
        self.cond_disable = cond_disable or []

    def visible(self, obj):
        return True

    @property
    def text(self):
        if isinstance(self.basetext, Accessor):
            basetext = self.basetext.resolve(self.obj)
        else:
            basetext = self.basetext
        return escape(basetext)

    @property
    def disabled(self):
        for cond in self.cond_disable:
            field = cond[0]
            if isinstance(field, Accessor):
                field = field.resolve(self.obj)

            if len(cond) == 3:
                cond_html = '{% if '
                if cond[1] == False:
                    cond_html += 'not '
                return cond_html+field+' %} disabled{% endif %}'

            if len(cond) > 1:
                if isinstance(cond[1], bool):
                    field = bool(field)
                return field == cond[1]

            return bool(field)

        return False

    @property
    def url(self):
        if self.viewname is None:
            return ""

        # The following params + if statements create optional arguments to
        # pass to Django's reverse() function.
        params = {}
        if self.args:
            params['args'] = [arg.resolve(self.obj)
                              if isinstance(arg, Accessor) else arg
                              for arg in self.args]
        if self.kwargs:
            params['kwargs'] = {}
            for key, value in self.kwargs.items():
                params['kwargs'][key] = (value.resolve(self.obj)
                                         if isinstance(value, Accessor) else value)
        if self.urlconf:
            params['urlconf'] = (self.urlconf.resolve(self.obj)
                                 if isinstance(self.urlconf, Accessor)
                                 else self.urlconf)
        if self.current_app:
            params['current_app'] = (self.current_app.resolve(self.obj)
                                     if isinstance(self.current_app, Accessor)
                                     else self.current_app)

        return reverse(self.viewname, **params)

    @property
    def attrs(self):
        if self.url:
            self.base_attrs["href"] = self.url

        if self.disabled:
            if isinstance(self.disabled, bool):
                self.base_attrs['class'] += ' disabled'
            else:
                self.base_attrs['class'] += self.disabled

        return self.base_attrs

    def render(self, obj, field=None):
        """ Render link as HTML output tag <a>.
        """
        self.obj = obj
        attrs = ' '.join([
            '%s="%s"' % (attr_name, attr.resolve(obj))
            if isinstance(attr, Accessor)
            else '%s="%s"' % (attr_name, attr)
            for attr_name, attr in self.attrs.items()
        ])
        html = ('<a %s>%s</a>' % (attrs, self.text)) if self.text else ''
        # html = '<a class="btn btn-primary">{{ perms.product.change_product }}</a>'
        print(html)
        template = Template(html)
        return template.render(Context({}))


class ImageLink(Link):
    """
    Represents a html <a> tag that contains <img>.
    """
    def __init__(self, field=None, image=None, image_title=None, static=False, attrs=None, attrs_image=None, *args,
                 **kwargs):
        self.field = field
        self.image_path = image
        self.image_title = image_title
        self.static = static
        self.base_attrs_image = attrs_image or {}
        super(ImageLink, self).__init__(attrs=attrs, *args, **kwargs)

    @property
    def url(self):
        path = Accessor(self.field).resolve(self.obj) if self.field else self.image_path
        if self.static:
            path = '{%% static "%s" %%}' % (path, )

        return path

    @property
    def attrs_image(self):
        if isinstance(self.image_title, Accessor):
            self.image_title = Accessor(self.field).resolve(self.obj)

        if self.image_title:
            self.base_attrs_image['title'] = self.image_title

        self.base_attrs_image['src'] = self.url
        return self.base_attrs_image

    @property
    def image(self):

        attrs = ' '.join([
            '%s="%s"' % (attr_name, attr.resolve(obj))
            if isinstance(attr, Accessor)
            else '%s="%s"' % (attr_name, attr)
            for attr_name, attr in self.attrs_image.items()
        ])
        html = ('{% load static %} <img %s>' % (attrs)) if self.static else ('<img %s>' % (attrs))
        template = Template(html)
        return template.render(Context())

    @property
    def text(self):
        return self.image
