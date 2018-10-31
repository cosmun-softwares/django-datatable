#!/usr/bin/env python
# coding: utf-8
import os
import imp
import time
import datetime

from django.utils.html import escape
from django.utils.safestring import mark_safe


class Accessor(object):
    """ A string describing a path from one object to another via attribute/index
        accesses. For convenience, the class has an alias `.A` to allow for more concise code.

        Relations are separated by a "." character.
    """
    SEPARATOR = '.'
    TYPES_DEFAULT = (int, str, datetime.datetime, datetime.date, datetime.time)

    def __init__(self, fields=None):
        if isinstance(fields, str):
            fields = [fields]
        self.fields = fields or []

    def resolve(self, context, delimiter=' ', quiet=False):
        """
        Return an object described by the accessor by traversing the attributes of context.
        """
        try:
            self.obj = context
            texts = []
            for field in self.fields:
                if '.' in field:
                    value = self.mont_list(field.split(self.SEPARATOR), self.obj)
                else:
                    value = self.get_value(field, self.obj)

                if value and isinstance(value, self.TYPES_DEFAULT):
                    texts.append(str(value))
                elif value:
                    return value
            return delimiter.join(texts)

        except Exception as e:
            if quiet:
                return ''
            else:
                raise e

    def mont_list(self, levels, obj):
        for level in levels:
            obj = self.get_value(level, obj)
            if not obj:
                break
        return obj


    def get_value(self, level, obj):
        if isinstance(obj, dict):
            obj = obj.get(level)
        elif isinstance(obj, list) or isinstance(obj, tuple):
            obj = obj[int(level)]
        else:
            if callable(getattr(obj, level)):
                try:
                    obj = getattr(obj, level)()
                except Exception:
                    obj = getattr(obj, level)
            else:
                # for model field that has choice set
                # use get_xxx_display to access
                display = 'get_%s_display' % level
                obj = getattr(obj, display)() if hasattr(obj, display) else getattr(obj, level)

        return obj


A = Accessor


class AttributesDict(dict):
    """
    A `dict` wrapper to render as HTML element attributes.
    """
    def render(self):
        return mark_safe(' '.join([
            '%s="%s"' % (attr_name, escape(attr))
            for attr_name, attr in self.items()
        ]))


def timeit(func):
    def wrap(*args, **kwargs):
        ts = time.time()
        result = func(*args, **kwargs)
        te = time.time()
        print('func: %r took: %f ms'.format(func.__name__, (te - ts) * 1000))
        return result
    return wrap


def load_class(full_class_string):
    """
    Dynamically load a class from a string

    >>> klass = load_class("module.submodule.ClassName")
    >>> klass2 = load_class("myfile.Class2")
    """
    class_data = full_class_string.split(".")

    module_str = class_data[0]
    class_str = class_data[-1]
    submodules_list = []

    if len(class_data) > 2:
        submodules_list = class_data[1:-1]

    f, filename, description = imp.find_module(module_str)
    module = imp.load_module(module_str, f, filename, description)

    # Find each submodule
    for smod in submodules_list:
        path = os.path.dirname(filename) if os.path.isfile(filename) else filename

        f, filename, description = imp.find_module(smod, [path])

        # Now we can load the module
        try:
            module = imp.load_module(" ".join(class_data[:-1]), f, filename, description)
        finally:
            if f:
                f.close()

    # Finally, we retrieve the Class
    return getattr(module, class_str)


def check_condition(object_list, obj, user):

    object_list = object_list or []
    results = []

    for cond in object_list:
        if cond.get('type_cond'):
            results.append(cond.get('type_cond'))
            break
        obj_1 = cond.get('obj_1')
        obj_2 = cond.get('obj_2')
        field_1 = obj_1.get('field')
        field_2 = obj_2.get('field')
        if isinstance(field_1, Accessor) and not obj_1.get('type'):
            field_1 = field_1.resolve(obj)
        if isinstance(field_2, Accessor) and not obj_2.get('type'):
            field_2 = field_2.resolve(obj)

        results.append(check_type(cond, user, obj_1, obj_2, field_1, field_2))

    if 'or' in results:
        return True if True in results else False
    else:
        return False if False in results else True


def check_type(cond, user, obj_1, obj_2, field_1, field_2):

    if obj_1.get('type') == 'perm':
        if cond.get('cond') and cond.get('cond') == 'not':
            return user.has_perm(field_1) != field_2
        else:
            return user.has_perm(field_1) == field_2
    elif obj_1.get('type') == 'user':
        if cond.get('cond') and cond.get('cond') == 'not':
            return Accessor(field_1).resolve(user) != field_2
        else:
            return Accessor(field_1).resolve(user) == field_2
    if obj_2.get('type') == 'perm':
        if cond.get('cond') and cond.get('cond') == 'not':
            return user.has_perm(field_2) != field_1
        else:
            return user.has_perm(field_2) == field_1
    elif obj_2.get('type') == 'user':
        if cond.get('cond') and cond.get('cond') == 'not':
            return Accessor(field_2).resolve(user) != field_1
        else:
            return Accessor(field_2).resolve(user) == field_1

    return bool(field_1) == field_2
