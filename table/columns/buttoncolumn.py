#!/usr/bin/env python
# coding: utf-8
import django

if django.VERSION >= (1, 10) and django.VERSION < (2, 1):
    from django.urls import reverse
elif django.VERSION >= (2, 1):
    from django.urls import reverse_lazy as reverse
else:
    from django.core.urlresolvers import reverse

from django.utils.html import escape
from django.utils.safestring import mark_safe

from table.utils import Accessor, check_condition
from table.columns.base import Column


class ButtonColumn(Column):
    def __init__(self, header=None, buttons=None, attrs=None, header_attrs=None, delimiter='&nbsp',
                 field=None, **kwargs):
        self.buttons = buttons
        self.delimiter = delimiter
        kwargs['safe'] = False
        kwargs["searchable"] = False
        super(ButtonColumn, self).__init__(field, header, attrs, header_attrs, **kwargs)

    def render(self, obj, user=None):
        return self.delimiter.join([
            button.render(obj, field=self.field, user=user)
            for button in self.buttons if button.visible(obj, user=user)
        ])


class Button(object):
    """
    Represents a html <button> tag.
    """
    def __init__(self, text=None, viewname=None, args=None, kwargs=None, urlconf=None, current_app=None, attrs=None,
                 modal_target=None, onclick=None, visible=None, disable=None):
        self.basetext = text
        self.viewname = viewname
        self.args = args or []
        self.kwargs = kwargs or {}
        self.urlconf = urlconf
        self.current_app = current_app
        self.base_attrs = attrs or {}
        self.modal_target = modal_target
        self.onclick = onclick
        self.cond_visible = visible or []
        self.cond_disable = disable or []

    def visible(self, obj, user=None):
        return check_condition(self.cond_visible, obj, user)

    @property
    def disabled(self):
        if self.cond_disable:
            return check_condition(self.cond_disable, self.obj, self.user)
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
        if self.onclick:
            self.base_attrs['onclick'] = f'{self.onclick}(\'{self.url}\')'

        if self.disabled:
            self.base_attrs['disabled'] = True
        else:
            if self.base_attrs.get('disabled'):
                del self.base_attrs['disabled']

        return self.base_attrs


    def render(self, obj, field=None, user=None):
        """ Render link as HTML output tag <button>.
        """
        self.obj = obj
        self.user = user
        if field:
            self.field = field
        attrs = ' '.join([
            '%s="%s"' % (attr_name, attr.resolve(obj))
            if isinstance(attr, Accessor)
            else '%s="%s"' % (attr_name, attr)
            for attr_name, attr in self.attrs.items()
        ])
        return mark_safe(u'<button %s>%s</button>' % (attrs, self.text))
