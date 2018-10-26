#!/usr/bin/env python
# coding: utf-8
from django.urls import path
from table.views import FeedDataView

app_name = 'datatable'

urlpatterns = [
    path('ajax/<str:token>/', FeedDataView.as_view(), name='feed_data'),
]
