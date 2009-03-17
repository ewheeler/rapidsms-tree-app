#!/usr/bin/env python
# vim: ai ts=4 sts=4 et sw=4


from django.db import models


class Question(models.Model):
    text = models.TextField()
    
    def __unicode__(self):
        return "Q%s: %s" % (
            self.pk,
            self.text)


class Tree(models.Model):
    trigger = models.CharField(max_length=30, help_text="The incoming message which triggers this Tree")
    root_question = models.ForeignKey(Question, related_name="first_question", help_text="The first Question sent when this Tree is triggered, which may lead to many more")
    
    def __unicode__(self):
        return "T%s: %s -> %s" % (
            self.pk,
            self.trigger,
            self.root_question)


class Answer(models.Model):
    previous_question = models.ForeignKey(Question, related_name="previous_question", help_text="The Question which this Answer is an option to")
    next_question     = models.ForeignKey(Question, blank=True, null=True, related_name="next_question", help_text="The (optional) Question to proceed to when this Answer is chosen")
    trigger           = models.CharField(max_length=30, help_text="The incoming message which triggers this Answer")
    response          = models.TextField(blank=True, help_text="The message which is sent in response to this Answer, before the next question is sent")
    
    def __unicode__(self):
        return ("Q%s -> %s" % (
            self.previous_question.pk,
            self.trigger) +\
            
            # if this question has a "next question", which the
            # user is forwarded to after answering, append it
            (" -> Q%s" % (self.next_question.pk)\
                if self.next_question else ""))
