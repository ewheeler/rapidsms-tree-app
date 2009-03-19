#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4

from django.conf.urls.defaults import *
import apps.tree.views as tv

urlpatterns = patterns('',
    url(r'alpha', tv.alpha),
    url(r'beta',  tv.beta),
    url(r'gamma', tv.gamma)
)
