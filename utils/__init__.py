# Various utility functions 
from django.http import HttpResponse
from django.template import RequestContext, Context, loader

def render_to_response(request, template, dictionary={}, context_instance=None, mimetype='text/html'):
	
	t = loader.get_template(template)
	c = RequestContext(request, dictionary)
	
	return HttpResponse(t.render(c), mimetype)