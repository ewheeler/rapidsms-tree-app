from django.template import Library
register = Library()

@register.inclusion_tag("partials/tree.html")
def render_tree(tree):
	return { "tree": tree }

@register.inclusion_tag("partials/question.html")
def render_question(question):
	return { "question": question }
