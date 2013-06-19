# Various utility functions
from django.http import HttpResponse
from django.template import RequestContext, loader


def render(request, template,
           dictionary={}, context_instance=None, mimetype='text/html'):

    t = loader.get_template(template)
    c = RequestContext(request, dictionary)

    return HttpResponse(t.render(c), mimetype)
