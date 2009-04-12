from django.template import Library
register = Library()

@register.inclusion_tag("tree/partials/tree.html")
def render_tree(tree):
	return { "tree": tree }

@register.inclusion_tag("tree/partials/question.html")
def render_question(question):
	return { "question": question }
