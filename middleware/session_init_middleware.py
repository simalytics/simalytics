class SessionInitMiddleware(object):
    def process_request(self, request):
        if not request.session.session_key:
			# Force the generation of a new session key
			print "Generating new session key"
			request.session.save()
			print "New session key: [%s]" % request.session.session_key
    
