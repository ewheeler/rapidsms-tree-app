#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response

from apps.tree.models import *

from StringIO import StringIO
import csv


def index(req):
    allTrees = Tree.objects.all()
    if len(allTrees) != 0:
		t = allTrees[len(allTrees) - 1]
		return render_to_response("tree/index.html",
		    { "trees": allTrees, "t": t },
		    context_instance=RequestContext(req))
    else:
		return render_to_response("tree/index.html",
		    context_instance=RequestContext(req))


def data(req, id = None):
    allTrees = Tree.objects.all()
    # ok, the plan is to generate a table of responses per state, but this is tricky with loops.
    # the first thing we'll do is get all the possible states you can reach from the tree
    # then we'll tabulate the results of each state as a total
    # then we'll look at paths, by using the concatenated list of states taken for that path as a key
    # but first things first.  let's get all the states you can reach
    if len(allTrees) != 0:
        t = get_tree(id)
        all_states = get_all_states(t)
        loops = has_loops(t) 
        if not loops:
            # this is the easy case.  just create one column per state and then display the results
            # print "==== all states === \n%s\n==== end all states ==== " % all_states
            # now we're going to build a data structure to hold the submissions.  
            # It's just going to be a list of lists, where each sub-list represents
            # a single submission.  We'll also keep a second list for the column headers
            sessions = Session.objects.all().filter(tree=t)
            return render_to_response("tree/data.html",
                                      { "trees": allTrees, "t": t, "states" : all_states, "sessions" : sessions },
                                      context_instance=RequestContext(req))
        else: 
            # todo
            pass
        print all_states
        # now we need to map all states to answers
        states_w_answers = {}
        for state in all_states:
            states_w_answers[state] = map((lambda x: x.answer), state.transition_set.all()) 
        print states_w_answers
        # now we need to get all the entries
        all_entries = Entry.objects.all().filter(session__tree = t)
        print all_entries
        if loops:
            # stupid error fix to prevent trees with loops from exploding.  This should be done better
            t = Tree()
            t.trigger = "Sorry, can't display this tree because it has loops.  We're working on it."
        return render_to_response("tree/index.html",
            { "trees": allTrees, "t": t },
            context_instance=RequestContext(req))
    else:
        return render_to_response("tree/index.html",
            context_instance=RequestContext(req))

def export(req, id = None):
    #print states
    #print sessions
    t = get_tree(id)
    all_states = get_all_states(t)
    loops = has_loops(t) 
    if not loops:
        output = StringIO()
        w = csv.writer(output)
        headings = ["Person", "Date"]
        headings.extend([state.question for state in all_states])
        w.writerow(headings)
        sessions = Session.objects.all().filter(tree=t)
        for session in sessions:
            values = [str(session.person), session.start_date]
            transitions = map((lambda x: x.transition), session.entry_set.all())
            states_w_transitions = {}
            for transition in transitions:
                states_w_transitions[transition.current_state] = transition
            #print states_w_transitions
            for state in all_states:
                if states_w_transitions.has_key(state):
                    values.append(states_w_transitions[state].answer)
                else:
                    values.append("")
            w.writerow(values)
            # rewind the virtual file
        output.seek(0)
        response = HttpResponse(output.read(),
                            mimetype='application/ms-excel')
        response["content-disposition"] = "attachment; filename=%s.csv" % t.trigger
        return response
    else:
        return render_to_response("tree/index.html",
                                  context_instance=RequestContext(req))
    


def add_all_unique_children(state, added):
    ''' Adds all unique children of the state to the passed in list.  This happens
        recursively.'''
    transitions = state.transition_set.all()
    #loops = False
    for transition in transitions:
        if transition.next_state:
            if not added.__contains__(transition.next_state):
                added.append(transition.next_state)
                add_all_unique_children(transition.next_state, added)
            #else:
                #loops = True
    #return loops
                
                
def has_loops(tree):
    return path_has_loops([tree.root_state])

def path_has_loops(path):
    # we're going to get all unique paths through the tree (or until we hit a loop)
    # a path is defined as an ordered set of states
    # if at any point in a path we reach a state we've already seen then we have a loop
    # this is basically a depth first search
    last_node = path[len(path) - 1]
    transitions = last_node.transition_set.all()
    for transition in transitions:
      if transition.next_state:
          # Base case.  We have already seen this state in the path
          if path.__contains__(transition.next_state):
              return True
          next_path = path[:]
          next_path.append(transition.next_state)
          # recursive case - there is a loop somewhere below this path
          if path_has_loops(next_path):
              return True
    # we trickle down to here - went all the way through without finding any loops
    return False
      
    
def get_tree(id):
    if id:
        return Tree.objects.get(id=id)
    else:
        return Tree.objects.all()[len(Tree.objects.all()) - 1]  
    
def get_all_states(tree):
    all_states = []
    all_states.append(tree.root_state)
    add_all_unique_children(tree.root_state, all_states)
    return all_states
        
    
    
    
    