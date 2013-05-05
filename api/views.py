# Create your views here.
import json

from django.http import HttpResponse
from visitor import visitor_utils
from api.models import Action
from content_profiles.models import ContentProfile
from pcu.models import PCU, PCUAction, PCUInteraction, PCUInteractionData,\
    PCUAnalytics, PCUStatus
from django.views.decorators.csrf import csrf_exempt              
from user_accounts.account_model import GuestSession     
from datetime import datetime
from traceback import print_exc
from pcu.key_management import generate_pcu_public_key
from user_accounts.session_management import generate_guest_session_ident
import api_util
from django.shortcuts import render_to_response

def generate_analytics(currentPcu, action, time):
    #hour = datetime(time.year,
    #                time.month,
    #                time.day,
    #                time.hour,
    #                0)
    
    recordHour = time.replace(
        minute = 0, 
        second = 0, 
        microsecond = 0)
        
    try:
        # Attempt to get an existing analytics record:
        record = None
        try:
            record = PCUAnalytics.objects.get(pcu = currentPcu, hour = recordHour) #pcu = currentPcu, hour = recordHour)
        except Exception, e:
            print_exc()
        
        if not record:
            print "NEW"
            record = PCUAnalytics()
            record.pcu = currentPcu
            record.hour = recordHour
        
        if action.code == "OVERLAY_REQUEST":
            record.overlayOpenClicks = (record.overlayOpenClicks + 1) if record.overlayOpenClicks else 1
        elif action.code == "CLICK_PAY":
            record.acceptClicks = (record.acceptClicks + 1) if record.acceptClicks else 1
        elif action.code == "CLICK_CANCEL":
            record.declineClicks = (record.declineClicks + 1) if record.declineClicks else 1
        elif action.code == "CLICK_MORE_INFO":
            record.moreInformationClicks = (record.moreInformationClicks + 1) if record.moreInformationClicks else 1
        
        #print "PRESAVE"
        #print record.hour
        record.save()
        
        #from django.db import connection
        #print connection.queries
        
        #print "ID %s" % record.id
    except Exception, e:
        print "Error storing analytics for PCU [%s], hour [%s]: %s" % (currentPcu.id, recordHour, e)
        print_exc()
        raise e

def store_pcu_interaction(request, guestSessionIdent, pcu, actionCode, userProfile):
    sessionId = guestSessionIdent
    try:
        guestSession = GuestSession.objects.get(externalIdent = sessionId)
    except Exception, e:
        print "Error retrieving guest session with external ident [%s]: %s" % (sessionId, e)
        return HttpResponse(status = 401)

    if not userProfile:
        try:
            userProfile = ContentProfile.objects.get(pk = guestSession.profile.id)
            print "Retrieved profile %s for guest session ID %s" % (userProfile.id, sessionId)
        except Exception, e:
            print "Error retrieving profile attached to guest session %s: %s" % (sessionId, e)
            return HttpResponse(status = 401)
    
    if pcu.profile.id != userProfile.id:
        return api_util.generate_response({ "error": "PCU not attached to profile" }, 401)
    
    if guestSession.profile != userProfile:
        print "Profile [%s] not attached to guest session [%s]" % (pcu.publicKey, guestSession.externalIdent)
        return HttpResponse(status = 401)
    
    try:
        try:
            action = PCUAction.objects.get(code = actionCode)
        except Exception, e:
            print "Error retrieving action for code [%s]: %s" % (actionCode, e)
            return api_util.generate_response({ "error": "Invalid action: [%s]" % actionCode }, 422)
        
        interaction = PCUInteraction()
        interaction.pcu = pcu
        interaction.action = action
        interaction.session = guestSession
        interaction.save()
        
        interactionData = PCUInteractionData()
        interactionData.interaction = interaction
        interactionData.httpHeaders = request.META
        interactionData.save()
        
        generate_analytics(pcu, action, datetime.now())
    except Exception, e:
        print "Error storing interaction with PCU [%s]: %s" % (pcu.publicKey, e)
        print_exc()
        return HttpResponse(status = 500)

@csrf_exempt 
def api_operation_pcu_register(request):
    print "PCU-Register"
    o = api_util.init_request(request, "POST")
    
    profile = api_util.get_profile(request)
    if profile == None:
        return HttpResponse(status = 401)
    
    if isinstance(o, HttpResponse):
        return o
    else:
        json = o
    
    if not api_util.check_keys(json, [ "url", "pcuIdentifier" ]):
        return HttpResponse(status = 422)
    
    url = json["url"]
    ident = json["pcuIdentifier"]
    
    # Get 'active' status
    activeStatus = None
    try:
        activeStatus = PCUStatus.objects.get(code = "ACTIVE")
    except Exception, e:
        print "Error retrieving ACTIVE status: %s" % e
        return HttpResponse(status = 500)
    
    # Store the new PCU
    pcu = PCU()
    pcu.url = url
    pcu.pcuIdentifier = ident
    pcu.profile = profile
    pcu.publicKey = generate_pcu_public_key(pcu)
    pcu.status = activeStatus
    pcu.save()
    
    return api_util.generate_response({ "Location": "%s" % pcu.publicKey }, 201)
    #return HttpResponse(mimetype="text/plain; Location: /api/opn/pcu/%s" % pcu.publicKey, status = 201)
@csrf_exempt 
def api_operation_pcu_delete(request, pcu_pub_key):
    print "PCU-Delete"
    o = api_util.init_request(request, "DELETE")
    if isinstance(o, HttpResponse):
        return o
    
    profile = api_util.get_profile(request)
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
    
    o = api_util.init_request(request, "GET")
    if isinstance(o, HttpResponse):
        return o
    
    userProfile = api_util.get_profile(request)
    if userProfile == None:
        return HttpResponse(status = 401)
    
    output = []
    
    profileUnits = PCU.objects.filter(profile = userProfile)
    for pcu in profileUnits:
        output.append({
            "url": pcu.url,
            "pcuIdentifier": pcu.pcuIdentifier,
            "publicKey": pcu.publicKey,
            "created": pcu.created           
        })

    return api_util.generate_response(output, 200)

@csrf_exempt    
def api_operation_pcu_get(request, pcu_pub_key):
    print "PCU-Get"
    
    o = api_util.init_request(request, "GET")
    if isinstance(o, HttpResponse):
        return o
    
    profile = api_util.get_profile(request)
    if profile == None:
        return HttpResponse(status = 400)
    
    try :
        pcu = PCU.objects.get(publicKey = pcu_pub_key, profile = profile)
    except Exception, e:
        print "Error retrieving PCU for public key [%s]: %s" % (pcu_pub_key, e)
        return HttpResponse(status = 401)
    
    responseObj = {
        "url": pcu.url,
        "pcuIdentifier": pcu.pcuIdentifier,
        "publicKey": pcu.publicKey,
        "created": pcu.created
    }
    
    return api_util.generate_response(responseObj, 200)
    
@csrf_exempt
def api_operation_pcu_visit(request, guest_session_id, url):
    # Page view
    print "PCU-Visit"

@csrf_exempt     
def api_operation_pcu_click(request, pcu_pub_key):
    print "PCU-Click"
    
    o = api_util.init_request(request, "POST")
    if isinstance(o, HttpResponse):
        return o
    else :
        json = o

    try:
        pcu = PCU.objects.get(publicKey = pcu_pub_key)
    except Exception, e:
        print "Error retrieving PCU for public key [%s]: %s" % (pcu_pub_key, e)
        
    if not api_util.check_keys(json, [ "guestSessionIdent", "action" ]):
        return HttpResponse(status = 422)
    
    sessionId = json["guestSessionIdent"]
    actionCode = json["action"]
    
    storeResponse = store_pcu_interaction(request, sessionId, pcu, actionCode, None)
    if storeResponse:
        return storeResponse
    else:
        return HttpResponse(status = 200)
    
@csrf_exempt 
def api_operation_render_overlay(request, pcu_pub_key):
    print "Render-Overlay"
    
    o = api_util.init_request(request, "POST")
    if isinstance(o, HttpResponse):
        return o
    else :
        json = o

    userProfile = api_util.get_profile(request)
    if userProfile == None:
        return HttpResponse(status = 401)
    
    try:
        pcu = PCU.objects.get(publicKey = pcu_pub_key, profile = userProfile)
    except Exception, e:
        print "Error retrieving PCU for public key [%s] belonging to profile [%s]: %s" % (pcu_pub_key, userProfile.privateKey, e)
        
    if not api_util.check_keys(json, [ "guestSessionIdent" ]):
        return HttpResponse(status = 422)
    
    guestSessionIdent = json["guestSessionIdent"];
    
    storeResponse = store_pcu_interaction(request, guestSessionIdent, pcu, "OVERLAY_REQUEST", userProfile)
    if storeResponse:
        return storeResponse
    else:
        return render_to_response("overlay/overlay_content.html", {
               "baseUrl": api_util.get_base_app_url(request)
        })

@csrf_exempt 
def api_operation_client_session_init(request):
    print "Client-Session-Init"
    o = api_util.init_request(request, "GET")
    
    if isinstance(o, HttpResponse):
        return o
    
    if request.META["HTTP_UNIT_KEY"]:
        pcuPublicKey = request.META["HTTP_UNIT_KEY"]
    else:
        return api_util.generate_response({ "error": "Missing unit key" }, 400)
    
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
        gSession.sourceIp = sourceIp
        gSession.externalIdent = generate_guest_session_ident(gSession)
        gSession.save()
    except Exception, e:
        print "Error saving guest session. %s" % e
        return HttpResponse(status = 500)
    
    return api_util.generate_response({ "sessionId": gSession.externalIdent }, 201)
