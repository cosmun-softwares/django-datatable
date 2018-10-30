#!/usr/bin/env python
# coding: utf-8
from datetime import datetime
from django.utils.html import escape

from table.utils import Accessor
from .base import Column


class DatetimeColumn(Column):

    DEFAULT_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self, field, header=None, format=None, default=None, **kwargs):
        self.format = format or self.DEFAULT_FORMAT
        super(DatetimeColumn, self).__init__(field, header, default=default, **kwargs)

    def render(self, obj, user=None):
        obj = Accessor(self.field).resolve(obj)
        if obj:
            if len(obj) > 11:
                format = self.format
                default_format = self.DEFAULT_FORMAT
            else:
                format = self.format[:8]
                default_format = self.DEFAULT_FORMAT[:8]

            obj = datetime.strptime(obj, default_format).strftime(format)
        return escape(obj) if obj else self.default


class DateColumn(DatetimeColumn):

    DEFAULT_FORMAT = "%Y-%m-%d"

    def __init__(self, field, header=None, format=None, default=None, **kwargs):
        format = format or self.DEFAULT_FORMAT
        super(DateColumn, self).__init__(field, header, format, default=default, **kwargs)

    def render(self, obj, user=None):
        obj = Accessor(self.field).resolve(obj)
        if obj:
            obj = datetime.strptime(obj, self.DEFAULT_FORMAT).strftime(self.format)
        return escape(obj) if obj else self.default


class TimeColumn(DatetimeColumn):

    DEFAULT_FORMAT = "%H:%M:%S"

    def __init__(self, field, header=None, format=None, default=None, **kwargs):
        format = format or self.DEFAULT_FORMAT
        super(TimeColumn, self).__init__(field, header, format, default=default, **kwargs)

    def render(self, obj, user=None):
        obj = Accessor(self.field).resolve(obj)
        if obj:
            obj = datetime.strptime(obj, self.DEFAULT_FORMAT).strftime(self.format)
        return escape(obj) if obj else self.default
