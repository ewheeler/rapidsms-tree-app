#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

from apps.tree.models import *


def alpha(req):
	return render_to_response("alpha.html", { },
	    context_instance=RequestContext(req))

def beta(req):
	return HttpResponse("BETA")

def gamma(req):
	return HttpResponse("GAMMA")
