#!/usr/bin/env python
# coding: utf-8
from django.template import Template, Context

from table.columns import Column
from table.utils import Accessor


class BoolColumn(Column):
    def __init__(self, field=None, header=None, *args, **kwargs):
        kwargs["sortable"] = False
        kwargs["searchable"] = False
        super(BoolColumn, self).__init__(field, header, *args, **kwargs)

    def render(self, obj):
        text = Accessor(self.field).resolve(obj)
        html = '<i class="fas '
        if text:
            html += 'fa-check-circle text-success'
        else:
            html += 'fa-times-circle text-danger'
        html += '"></i>'
        template = Template(html)
        return template.render(Context())
