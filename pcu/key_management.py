import uuid

def generate_pcu_public_key(pcu):
    print "PCU Public Key generator"
    #return int(round(time.time() * 1000))  # TODO: FIX!
    return uuid.uuid4().int