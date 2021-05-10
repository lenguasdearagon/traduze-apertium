from django import template


register = template.Library()


@register.filter
def get_language(languages, lang_code):
	for code, language in languages:
		if code == lang_code:
			return language