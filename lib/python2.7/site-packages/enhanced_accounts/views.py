# Create your views here.
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render_to_response
from django.template.context import RequestContext
from enhanced_accounts.forms import EnhancedLoginMiniForm

def index(request):
    if request.user and request.user.id:

        return redirect(reverse('content_profiles_list'))

    else:
        form = EnhancedLoginMiniForm()

    return render_to_response('index.html',
        {'form': form},
        context_instance=RequestContext(request)
    )

# {'form': AuthenticationForm(), 'r_form':UserCreationForm()}