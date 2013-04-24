import uuid

def generate_profile_private_key(profile):
    print "Key generator"
    #return int(round(time.time() * 1000))  # TODO: FIX!
    return uuid.uuid4().int