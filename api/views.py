# Create your views here.
import json

from django.http import HttpResponse
from visitor import visitor_utils
from api.models import Action
from content_profiles.models import ContentProfile
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, Http404
from pcu.pcu_model import PCU
from django.views.decorators.csrf import csrf_exempt              
from django.contrib.sites.models import Site                            

def init_request(request, expectedMethod):
    if (request.method != expectedMethod):
        #print "URL [%s] expected method [%s], received [%s]" % request.path % expectedMethod % request.method
        return HttpResponse(status = 405)

    try :
        if len(request.body) > 0:
            return json.loads(request.body)
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
    for key in expectedKeys:
        if not key in json:
            print "Missing key: [%s]" % key
            return False
        
    return True

def api_operation_see(request, profile_id):
    callback = request.GET.get('callback', '')
    req = {}
    request.session['visited'] = True
    try:
        profile = ContentProfile.objects.get(pk = profile_id)
        action = Action(profile = profile, is_seen = True)
        visitor = visitor_utils.get_visitor_from_request(request)
        action.visitor = visitor
        action.save()
        req ['result'] = 'success'
        req ['seen_id'] = action.id
    except Exception, e:
        req ['result'] = 'error'
    response = json.dumps(req)
    response = callback + '(' + response + ');'
    return HttpResponse(response, mimetype="application/json")

def api_operation_read(request, profile_id, action_id):
    callback = request.GET.get('callback', '')
    req = {}
    try:
        visitor = visitor_utils.get_visitor_from_request(request)
        profile = ContentProfile.objects.get(pk = profile_id)
        action = Action.objects.get(id=action_id, profile = profile, visitor=visitor, is_read = False)
        action.is_read = True
        action.save()
        req ['result'] = 'success'
        req ['content'] = profile.content
    except Exception, e:
        req ['result'] = 'error'
    response = json.dumps(req)
    response = callback + '(' + response + ');'
    return HttpResponse(response, mimetype="application/json")

@csrf_exempt 
def api_operation_profile_create(request):
    print "Profile-Create"
    
@csrf_exempt 
def api_operation_profile_delete(request, profile_id):
    print "Profile-Delete"

@csrf_exempt 
def api_operation_pcu_register(request):
    print "PCU-Register"
    o = init_request(request, "POST")
    
    profile = get_profile(request)
    if profile == None:
        return HttpResponse(status = 401)
    
    if isinstance(o, HttpResponse):
        return o
    else :
        json = o
    
    if not check_keys(json, [ "url", "pcuIdentifier" ]):
        return HttpResponse(status = 422)
    
    url = json["url"]
    ident = json["pcuIdentifier"]
    
    # Store the new PCU
    pcu = PCU()
    pcu.url = url
    pcu.publicKey = "<placeholder>"
    pcu.pcuIdentifier = ident
    pcu.profile = profile
    pcu.save()
    
    return HttpResponse(mimetype="text/plain; Location: /api/opn/pcu/%d" % pcu.id, status = 201)
@csrf_exempt 
def api_operation_pcu_delete(request, pcu_id):
    print "PCU-Delete"
    o = init_request(request, "DELETE")
    if isinstance(o, HttpResponse):
        return o
    
    profile = get_profile(request)
    if profile == None:
        return HttpResponse(status = 401)
    
    try :
        pcu = PCU.objects.get(pk = pcu_id)
    except Exception, e:
        print "Error obtaining PCU [%d]: %s" % pcu_id % e
        return HttpResponse(status = 401) # Mask the fact that the PCU does not exist.
    
    if pcu:
        if pcu.profile.id == profile.id:
            pcu.delete()
        else:
            return HttpResponse(status = 401)
        
    return HttpResponse(status = 200)
    
@csrf_exempt 
def api_operation_pcu_visit(request, pcu_id):
    # a.k.a Click
    print "PCU-Visit"

def api_operation_render_overlay(request, pcu_id):
    print "Render-Overlay"

@csrf_exempt 
def api_operation_client_session_init(request):
    print "Client-Session-Init"
