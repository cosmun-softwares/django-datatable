#!/usr/bin/env python
# coding: utf-8

from django.utils.html import escape
from django.utils.safestring import mark_safe

from table.utils import Accessor
from table.columns.base import Column


class ButtonColumn(Column):
    def __init__(self, header=None, buttons=None, attrs=None, header_attrs=None, delimiter='&nbsp',
                 field=None, **kwargs):
        self.buttons = buttons
        self.delimiter = delimiter
        kwargs['safe'] = False
        kwargs["searchable"] = False
        super(ButtonColumn, self).__init__(field, header, attrs, header_attrs, **kwargs)

    def render(self, obj):
        return self.delimiter.join([button.render(obj, self.field) for button in self.buttons])


class Button(object):
    """
    Represents a html <button> tag.
    """
    def __init__(self, text=None, viewname=None, args=None, kwargs=None, urlconf=None, current_app=None, attrs=None,
                 modal_target=None):
        self.basetext = text
        self.viewname = viewname
        self.args = args or []
        self.kwargs = kwargs or {}
        self.urlconf = urlconf
        self.current_app = current_app
        self.base_attrs = attrs or {}
        self.modal_target = modal_target
        self.field = None

    @property
    def text(self):
        if isinstance(self.basetext, Accessor):
            basetext = self.basetext.resolve(self.obj)
        else:
            basetext = self.basetext
        return escape(basetext)


    @property
    def attrs(self):
        if self.modal_target and getattr(self.obj, self.field):
            self.base_attrs['data-toggle'] = 'modal'
            self.base_attrs['data-target'] = '#'+self.modal_target+'-'+str(getattr(self.obj, self.field))
        return self.base_attrs


    def render(self, obj, field=None):
        """ Render link as HTML output tag <button>.
        """
        self.obj = obj
        if field:
            self.field = field
        attrs = ' '.join([
            '%s="%s"' % (attr_name, attr.resolve(obj))
            if isinstance(attr, Accessor)
            else '%s="%s"' % (attr_name, attr)
            for attr_name, attr in self.attrs.items()
        ])
        return mark_safe(u'<button %s>%s</button>' % (attrs, self.text))
