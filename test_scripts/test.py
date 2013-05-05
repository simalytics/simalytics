from urllib2 import Request, urlopen
import random
import json
import time

base_url = "http://localhost:8000"
profileKey = "150112892977307470685437840037046934171"

def create_pcu(base, profileKey, page):
    pageUrl = "http://localhost/%s" % page

    req = Request(
        url = "%s/api/opn/pcu/register" % base,
        data = "{ \"url\": \"%s\", \"pcuIdentifier\": \"PAGE1\" }" % pageUrl,
        headers = { "PROFILE_KEY": profileKey })
    req.get_method = lambda: "POST"

    data = urlopen(req)

    parsed = json.loads(data.read())

    #print parsed

    return parsed["Location"]

def get_session_key(base, pcuKey):
    req = Request(
        url = "%s/api/opn/pcu/session" % base,
        headers = { "UNIT_KEY": pcuKey })
    req.get_method = lambda: "GET"

    data = urlopen(req)
    
    parsed = json.loads(data.read())
    return parsed["sessionId"]

def get_overlay(base, sessionId, pcuKey, profileKey):
    req = Request(
        url = "%s/api/opn/pcu/%s/overlay" % (base, pcuKey),
        headers = { "PROFILE_KEY": profileKey },
        data = "{ \"guestSessionIdent\": \"%s\" }" % sessionId)
    req.get_method = lambda: "POST"

    data = urlopen(req)
    
    #parsed = json.loads(data.read())
    #return parsed["clickUrl"]

    return data.read()

def click(base, sessionId, pcuKey, action):
    req = Request(
        url = "%s/api/opn/pcu/%s/click" % (base, pcuKey),
        data = "{ \"guestSessionIdent\": \"%s\", \"action\": \"%s\" }" % (sessionId, action))
    req.get_method = lambda: "POST"

    data = urlopen(req)

print "Generating two PCUs..."

pcuKeys = {}
pcuKeys["page1"] = create_pcu(base_url, profileKey, "1.html")
time.sleep(5)
pcuKeys["page2"] = create_pcu(base_url, profileKey, "2.html")

print "Generated PCU keys:\n\t%s\n\t%s\n" % (pcuKeys["page1"], pcuKeys["page2"])

clickActions = [ "CLICK_PAY", "CLICK_CANCEL", "CLICK_MORE_INFO" ]

reqCount = 100#500

for i in range(reqCount):
    pcuKey = pcuKeys[random.choice(pcuKeys.keys())]

    sessionId = get_session_key(base_url, pcuKey)
    print "Retrieved session ID %s " % sessionId

    # Request overlay
    overlay_content = get_overlay(base_url, sessionId, pcuKey, profileKey)
    # Overlay content is not actually used

    # Simulate a click...but what could it be?!
    action = random.choice(clickActions)

    print "Simulating click: %s" % action

    click(base_url, sessionId, pcuKey, action)
