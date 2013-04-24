import uuid

def generate_guest_session_ident(guestSession):
    print "Session ID generator"
    #return int(round(time.time() * 1000))  # TODO: FIX!
    return uuid.uuid4().int