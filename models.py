#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.db import models
from apps.reporters.models import Reporter, PersistantConnection
import re


class Question(models.Model):
    text = models.TextField()
    
    def __unicode__(self):
        return "Q%s: %s" % (
            self.pk,
            self.text)


class Tree(models.Model):
    trigger = models.CharField(max_length=30, help_text="The incoming message which triggers this Tree")
    #root_question = models.ForeignKey("Question", related_name="tree_set", help_text="The first Question sent when this Tree is triggered, which may lead to many more")
    # making this compatible with the UI
    root_state = models.ForeignKey("TreeState", null=True, blank=True, related_name="tree_set", help_text="The first Question sent when this Tree is triggered, which may lead to many more")
    
    def __unicode__(self):
        return "T%s: %s -> %s" % (
            self.pk,
            self.trigger,
            self.root_state)


class Answer(models.Model):
    previous_question = models.ForeignKey(Question, related_name="answers", help_text="The Question which this Answer is an option to")
    trigger = models.CharField("Answer", max_length=30, help_text="The incoming message which triggers this Answer")
    next_question     = models.ForeignKey(Question, blank=True, null=True, related_name="next_question_set", help_text="The (optional) Question to proceed to when this Answer is chosen")
    response          = models.TextField(blank=True, help_text="The message which is sent in response to this Answer, before the next question is sent")
    
    def __unicode__(self):
        return ("Q%s -> %s" % (
            self.question.pk,
            self.answer))
            
            # if this question has a "next question", which the
            # user is forwarded to after answering, append it
            #(" -> Q%s" % (self.next_question.pk)\
            #    if self.next_question else ""))
        

class TreeState(models.Model):
    #tree = models.ForeignKey(Tree)
    name = models.CharField(max_length=100)
    question = models.ForeignKey(Question, blank=True, null=True)
    
    def __unicode__(self):
        return ("State %s, Question: %s" % (
            self.name,
            self.question))
    
class Transition(models.Model):
    TRANSITION_TYPES = (
        ('A', 'Answer (exact)'),
        ('R', 'Regular Expression'),
        ('C', 'Custom logic'),
    )
    current_state = models.ForeignKey(TreeState)
    type = models.CharField(max_length=1, choices=TRANSITION_TYPES)
    # I'm not sure if it's easier or harder to make this an Answer or just a CharField.  Leaving as a charfield for now.
    answer = models.CharField(max_length=160)
    description = models.CharField(max_length=50, null=True)
    next_state = models.ForeignKey(TreeState, blank=True, null=True, related_name='next_state')     
    
    def helper_text(self):
        if self.type == "A":
            if self.description:
                return "%s (%s)" % (self.answer, self.description)
            return self.answer
        if self.type == "R":
            if self.description:
                return self.description
            # this will be ugly
            return self.answer
        if self.type == "C":
            if self.description:
                return self.description
            # this might be ugly
            return self.answer
    

    def __unicode__(self):
        return ("%s : %s --> %s" % 
            (self.current_state,
             self.answer,
             self.next_state))
 
class Session(models.Model):
    # We might want to make these reporters
    connection = models.ForeignKey(PersistantConnection)
    tree = models.ForeignKey(Tree)
    start_date = models.DateTimeField(auto_now_add=True)
    state = models.ForeignKey(TreeState, blank=True, null=True) # none if the session is complete
     
    def __unicode__(self):
        if self.state:
            text = self.state
        else:
            text = "completed"
        return ("%s : %s" % (self.connection.identity, text))

class Entry(models.Model):
    session = models.ForeignKey(Session)
    sequence_id = models.IntegerField()
    transition = models.ForeignKey(Transition)
    time = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=160)
    
    def __unicode__(self):
        return "%s-%s: %s - %s" % (self.session.id, self.sequence_id, self.transition.current_state.question, self.text)
    
    def meta_data(self):
        return "%s - %s %s" % (
            self.session.person.phone,
            self.time.strftime("%a %b %e"),
            self.time.strftime("%I:%M %p"))
    
    def display_text(self):
        # assume that the display text is just the text,
        # since this is what it is for free text entries
        return self.text
    
    
    class Meta:
        verbose_name_plural="Entries"

'''class Message(models.Model):
    connection = models.CharField(max_length=100, blank=True, null=True)
    time = models.DateTimeField(auto_now_add=True)
    text = models.CharField(max_length=160)
    is_outgoing = models.BooleanField()

    def __unicode__(self):
        return self.text

'''