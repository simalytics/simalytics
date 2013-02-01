# Create your views here.
import json

from django.http import HttpResponse
from visitor import visitor_utils
from api.models import Action
from content_profiles.models import ContentProfile
from django.shortcuts import render_to_response

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
