from django.template import Template, Context

from django.utils.safestring import mark_safe
from table.utils import Accessor
from table.columns.linkcolumn import ImageLink
from table.columns.base import Column

class ImageSequenceColumn(Column):
    """
    Represents a html <a> tag that contains <img>.
    """
    def __init__(self, field, header, field_url, static=False, attrs=None, class_col=None, attrs_image=None, **kwargs):
        self.static = static
        self.class_col = class_col or 'col'
        self.field_url = field_url
        self.attrs_image = attrs_image or {}
        kwargs['safe'] = False
        kwargs["searchable"] = False
        super(ImageSequenceColumn, self).__init__(field, header, attrs=attrs, **kwargs)

    def render(self, obj, user=None):
        html_images = ''.join([
            '<div class="'+self.class_col+'">'+ ImageLink(
                field=self.field_url,
                static=self.static,
                attrs=self.attrs,
                attrs_image=self.attrs_image
            ).render(image) + '</div>'
            for image in Accessor(self.field).resolve(obj)
        ])
        return mark_safe('<div class="row">'+html_images+'</div>')
