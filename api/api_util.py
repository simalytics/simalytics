from django.http import HttpResponse
import json
from content_profiles.models import ContentProfile
from django.contrib.sites.models import Site

def init_request(request, expectedMethod):
    if (request.method != expectedMethod):
        print "URL [%s] expected method [%s], received [%s]" % (request.path, expectedMethod, request.method)
        return HttpResponse(status = 405)

    try :
        if len(request.body) > 0:
            return json.loads(request.body)
        else:
            print "No request body."
    except Exception, e:
        print "Error parsing JSON: [%s]" % e.message
        return HttpResponse(status = 400)

def get_profile(request):
    key = request.META["HTTP_PROFILE_KEY"]
    
    print "Received profile PRIVATE KEY [%s]" % key
    
    try:
        profile = ContentProfile.objects.get(privateKey = key)
    except Exception, e:
        print e
        return None
    
    return profile

def check_keys(json, expectedKeys):
    if not json and len(expectedKeys) == 0:
        return True
    elif not json and len(expectedKeys) > 0:
        return False
    
    for key in expectedKeys:
        if not key in json:
            print "Missing key: [%s]" % key
            return False
        
    return True

def generate_response(obj, statusCode):
    return HttpResponse(json.dumps(obj), "application/json", status = statusCode)

def get_base_app_url(request):
    return "http://%s" % request.get_host()