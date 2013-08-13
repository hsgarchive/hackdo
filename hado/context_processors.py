from django.conf import settings


def globals(request):
    SITE_ID = getattr(settings, 'SITE_ID', 1)
    if SITE_ID == 1:
        UA_ID = 'main site ua id'
    elif SITE_ID == 2:
        UA_ID = 'UA-32359827-2'
    else:
        UA_ID = None
    return {"UA_ID": UA_ID}
