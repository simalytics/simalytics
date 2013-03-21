# Create your views here.
import json

from django.http import HttpResponse
from visitor import visitor_utils
from api.models import Action
from content_profiles.models import ContentProfile
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect, Http404
from pcu.pcu_model import PCU, PCUAction, PCUInteraction, PCUInteractionData
from django.views.decorators.csrf import csrf_exempt              
from django.contrib.sites.models import Site
from user_accounts.account_model import GuestSession                            

def init_request(request, expectedMethod):
    if (request.method != expectedMethod):
        print "URL [%s] expected method [%s], received [%s]" % (request.path, expectedMethod, request.method)
        return HttpResponse(status = 405)

    try :
        print request.body
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

def store_pcu_interaction(request, guestSessionIdent, pcu, actionCode, userProfile):
    if userProfile != None and pcu.profile.id != userProfile.id:
        return generate_response({ "error": "PCU not attached to profile" }, 401)
    
    sessionId = guestSessionIdent
    try:
        guestSession = GuestSession.objects.get(externalIdent = sessionId)
    except Exception, e:
        print "Error retrieving guest session with external ident [%s]: %s" % (sessionId, e)
        return HttpResponse(status = 401)
    
    if userProfile != None and guestSession.profile != userProfile:
        print "Profile [%s] not attached to guest session [%s]" % (pcu.publicKey, guestSession.externalIdent)
        return HttpResponse(status = 401)
    
    try:
        try:
            action = PCUAction.objects.get(code = actionCode)
        except Exception, e:
            print "Error retrieving action for code [%s]: %s" % (actionCode, e)
            return generate_response({ "error": "Invalid action: [%s]" % actionCode }, 422)
        
        interaction = PCUInteraction()
        interaction.pcu = pcu
        interaction.action = action
        interaction.session = guestSession
        interaction.save()
        
        interactionData = PCUInteractionData()
        interactionData.interaction = interaction
        interactionData.httpHeaders = request.META
        interactionData.save()
    except Exception, e:
        print "Error storing interaction with PCU [%s]: %s" % (pcu.publicKey, e)
        return HttpResponse(status = 500)

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
    else:
        json = o
    
    if not check_keys(json, [ "url", "pcuIdentifier" ]):
        return HttpResponse(status = 422)
    
    url = json["url"]
    ident = json["pcuIdentifier"]
    
    # Store the new PCU
    pcu = PCU()
    pcu.url = url
    pcu.publicKey = "<placeholder>" # TODO: generate!
    pcu.pcuIdentifier = ident
    pcu.profile = profile
    pcu.save()
    
    return generate_response()
    return HttpResponse(mimetype="text/plain; Location: /api/opn/pcu/%s" % pcu.publicKey, status = 201)
@csrf_exempt 
def api_operation_pcu_delete(request, pcu_pub_key):
    print "PCU-Delete"
    o = init_request(request, "DELETE")
    if isinstance(o, HttpResponse):
        return o
    
    profile = get_profile(request)
    if profile == None:
        return HttpResponse(status = 401)
    
    try :
        pcu = PCU.objects.get(publicKey = pcu_pub_key)
    except Exception, e:
        print "Error obtaining PCU [%d]: %s" % pcu_pub_key % e
        return HttpResponse(status = 401) # Mask the fact that the PCU does not exist.
    
    if pcu:
        if pcu.profile.id == profile.id:
            pcu.delete()
        else:
            return HttpResponse(status = 401)
        
    return HttpResponse(status = 200)
    
@csrf_exempt
def api_operation_pcu_list(request):
    print "PCU-List"
    
    o = init_request(request, "GET")
    if isinstance(o, HttpResponse):
        return o
    
    userProfile = get_profile(request)
    if userProfile == None:
        return HttpResponse(status = 401)
    
    output = []
    
    profileUnits = PCU.objects.filter(profile = userProfile)
    for pcu in profileUnits:
        output.append({
            "url": pcu.url,
            "pcuIdentifier": pcu.pcuIdentifier,
            "publicKey": pcu.publicKey
            #"created": pcu.created           
        })

    return generate_response(output, 200)

@csrf_exempt    
def api_operation_pcu_get(request, pcu_pub_key):
    print "PCU-Get"
    
    o = init_request(request, "GET")
    if isinstance(o, HttpResponse):
        return o
    
    profile = get_profile(request)
    if profile == None:
        return HttpResponse(status = 400)
    
    try :
        pcu = PCU.objects.get(publicKey = pcu_pub_key)
    except Exception, e:
        print "Error retrieving PCU for public key [%s]: %s" % (pcu_pub_key, e)
        return HttpResponse(status = 401)
    
    responseObj = {
        "url": pcu.url,
        "pcuIdentifier": pcu.pcuIdentifier,
        "publicKey": pcu.publicKey,
        "created": pcu.created
    }
    
    return generate_response(responseObj, 200)
    
@csrf_exempt
def api_operation_pcu_visit(request, guest_session_id, url):
    # Page view
    print "PCU-Visit"

@csrf_exempt     
def api_operation_pcu_click(request, pcu_pub_key):
    print "PCU-Click"
    
    o = init_request(request, "POST")
    if isinstance(o, HttpResponse):
        return o
    else :
        json = o

    try:
        pcu = PCU.objects.get(publicKey = pcu_pub_key)
    except Exception, e:
        print "Error retrieving PCU for public key [%s]: %s" % (pcu_pub_key, e)
        
    if not check_keys(json, [ "guestSessionIdent", "action" ]):
        return HttpResponse(status = 422)
    
    sessionId = json["guestSessionIdent"]
    actionCode = json["action"]
    
    storeResponse = store_pcu_interaction(request, sessionId, pcu, actionCode, None)
    if storeResponse:
        return storeResponse
    else:
        return generate_response({
              "clickUrl": "/api/opn/pcu/%s/click" % pcu_pub_key
        }, 200)
    
    return generate_response({
          "clickUrl": "/api/opn/pcu/%s/click" % pcu_pub_key
    }, 200)
    
@csrf_exempt 
def api_operation_render_overlay(request, pcu_pub_key):
    print "Render-Overlay"
    
    o = init_request(request, "POST")
    if isinstance(o, HttpResponse):
        return o
    else :
        json = o

    userProfile = get_profile(request)
    if userProfile == None:
        return HttpResponse(status = 401)
    
    try:
        pcu = PCU.objects.get(publicKey = pcu_pub_key)
    except Exception, e:
        print "Error retrieving PCU for public key [%s]: %s" % (pcu_pub_key, e)
        
    if not check_keys(json, [ "guestSessionIdent" ]):
        return HttpResponse(status = 422)
    
    guestSessionIdent = json["guestSessionIdent"];
    
    storeResponse = store_pcu_interaction(request, guestSessionIdent, pcu, "OVERLAY_REQUEST", userProfile)
    if storeResponse:
        return storeResponse
    else:
        return generate_response({
              "clickUrl": "/api/opn/pcu/%s/click" % pcu_pub_key
        }, 200)

@csrf_exempt 
def api_operation_client_session_init(request):
    print "Client-Session-Init"
    o = init_request(request, "GET")
    
    if isinstance(o, HttpResponse):
        return o
    
    if request.META["HTTP_UNIT_KEY"]:
        pcuPublicKey = request.META["HTTP_UNIT_KEY"]
    else:
        return generate_response({ "error": "Missing unit key" }, 400)
    
    sourceIp = request.META["REMOTE_ADDR"]
    
    print "Generating session from %s for PCU pub key %s." % (sourceIp, pcuPublicKey)
    
    try:
        pcu = PCU.objects.get(publicKey = pcuPublicKey)
    except Exception, e:
        print "Error retrieving PCU with public key [%s]: %s" % (pcuPublicKey, e)
        return HttpResponse(status = 401)
    
    # Generate & store the session
    try:
        gSession = GuestSession()
        gSession.profile = pcu.profile
        gSession.externalIdent = "<placeholder>"
        gSession.sourceIp = sourceIp
        gSession.save()
    except Exception, e:
        print "Error saving guest session. %s" % e
        return HttpResponse(status = 500)
    
    return generate_response({ "sessionId": gSession.externalIdent }, 201)
