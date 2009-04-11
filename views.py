#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

from apps.tree.models import *


def index(req):
    allTrees = Tree.objects.all()
    if len(allTrees) != 0:
		t = allTrees[1]
		return render_to_response("tree/index.html",
		    { "trees": allTrees, "t": t },
		    context_instance=RequestContext(req))
    else:
		return render_to_response("tree/index.html",
		    context_instance=RequestContext(req))
