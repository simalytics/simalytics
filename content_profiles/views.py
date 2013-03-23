# Create your views here.
from datetime import datetime, timedelta
from django.conf import settings
from api import ACTION_TYPES
from api.models import Action
from content_profiles.forms import ContentProfileAddForm
from content_profiles.models import ContentProfile, ContentProfileStatus
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db.models.aggregates import Count, Sum
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
import logging
from bs4 import BeautifulSoup
import urllib
import time
from pcu.pcu_model import PCUAnalytics
from pcu.pcu_model import PCU
from traceback import print_exc

import inspect

def generate_stats(analytics):
    daysago6 = datetime.today() - timedelta(days=6)
    curdate = daysago6
    pstats = list()
    
    for stat in analytics:
        gapsize = (stat.hour - curdate).days
        if gapsize > 0:
            dategap = [curdate + timedelta(days=x) for x in range(0, gapsize + 1)]
            for dg in [datetime.strftime(x, '%b %d') for x in dategap]:
                pstats.append({
                       'action_datetime':dg, 
                       'overlayOpenClicks': 0, 
                       'acceptClicks': 0,
                       'declineClicks': 0,
                       'moreInformationClicks': 0
                })
    
        rectime = stat.hour
        rectimestr = datetime.strftime(rectime, '%b %d')
        pstats.append({
                       'action_datetime':rectimestr, 
                       'overlayOpenClicks': stat.overlayOpenClicks if stat.overlayOpenClicks else 0, 
                       'acceptClicks': stat.acceptClicks if stat.acceptClicks else 0,
                       'declineClicks': stat.declineClicks if stat.declineClicks else 0,
                       'moreInformationClicks': stat.moreInformationClicks if stat.moreInformationClicks else 0
        })
        curdate = stat.hour + timedelta(days=1)
    
        gapsize = (datetime.today() - curdate).days
        if gapsize > 0:
            dategap = [curdate + timedelta(days=x) for x in range(0, gapsize + 1)]
            for dg in [datetime.strftime(x, '%b %d') for x in dategap]:
                pstats.append({
                           'action_datetime':dg, 
                           'overlayOpenClicks': 0, 
                           'acceptClicks': 0,
                           'declineClicks': 0,
                           'moreInformationClicks': 0
                })
        else:
            gapsize = (datetime.today() - daysago6).days
            if gapsize > 0:
                dategap = [curdate + timedelta(days=x) for x in range(0, gapsize + 1)]
                for dg in [datetime.strftime(x, '%b %d') for x in dategap]:
                    pstats.append({
                               'action_datetime':dg, 
                               'overlayOpenClicks': 0, 
                               'acceptClicks': 0,
                               'declineClicks': 0,
                               'moreInformationClicks': 0
                    })
    
    return pstats

@login_required()
def content_profile_list(request):
    content_profiles_full = ContentProfile.objects.filter(created_by=request.user)
    paginator = Paginator(content_profiles_full, settings.PROFILES_PER_PAGE)
    page = request.GET.get('page')
    try:
        content_profiles = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        content_profiles = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        content_profiles = paginator.page(paginator.num_pages)

    request.breadcrumbs([
        ('Profiles', ''),
    ])

    return render_to_response('content_profiles/content_profile_list.html',
        {'content_profiles': content_profiles},
        context_instance=RequestContext(request)
    )

@login_required()
def content_profile_add(request):
    content_profile_form = ContentProfileAddForm()
    if request.POST:
        content_profile_form = ContentProfileAddForm(request.POST)

        if content_profile_form.is_valid():
            new_profile = content_profile_form.save(commit=False)
            new_profile.created_by = request.user

            # Retrieve page title
            pageStructure = BeautifulSoup(urllib.urlopen(new_profile.url));
            if not pageStructure:
                # TODO return helpful error message to client
                print "Could not retrieve"
            title = pageStructure.head.title
            if not title:
                # TODO return helpful error message to client
                print "Could not retrieve title for %s" % new_profile.url
            
            new_profile.name = title.renderContents()
            
            # Private key generation (currently just sys time)
            pKey = int(round(time.time() * 1000))  # TODO: FIX!
            new_profile.privateKey = pKey

            new_profile.status = 0

            new_profile.save()

            return HttpResponseRedirect(reverse('content_profiles_list'))
        else:
            print "Invalid form submitted"
            # TODO return helpful error message to client
    request.breadcrumbs([
        ("Profiles", reverse('content_profiles_list')),
        ('New Profile', ''),
    ])

    return render_to_response('content_profiles/content_profile_add.html',
        {'form': content_profile_form},
        context_instance=RequestContext(request)
    )

@login_required()
def content_profile_view(request, id):
    print "Viewing %s" % id
    
    try:
        content_profile = ContentProfile.objects.get(pk=id)
        if not content_profile:
            return Http404()
        
        
        stats = None  # Action.objects.filter(profile=content_profile.pk, action_datetime__gte=daysago6,action_datetime__lte=datetime.today()).extra({'action_datetime' : "date(action_datetime)"}).values('action_datetime').annotate(seen=Sum('is_seen'),read=Sum('is_read')).order_by('action_datetime')
        pstats = list()
        
        
        profilePcus = PCU.objects.filter(profile = content_profile)
        print "Retrieved %d PCUs for profile %d" % (len(profilePcus), content_profile.id)
        
        stats = PCUAnalytics.objects.filter(pcu__in = profilePcus)
        
        print "Stats: %d" % len(stats)
        
        if stats:
            graphData = generate_stats(stats)

    except Exception, e:
        # TODO: replace with proper logging! :@
        print "Error retrieving profile! [%s]" % e
        print_exc()
        raise Http404

    request.breadcrumbs([
        ("Profiles", reverse('content_profiles_list')),
        (content_profile.name, ''),
    ])

    return render_to_response('content_profiles/content_profile_view.html', {
            'content_profile': content_profile,
            'pcu_entities': profilePcus,
            'pstats': graphData if graphData else None
        },
        context_instance=RequestContext(request))

@login_required()
def content_profile_drop(request, id):
    try:
        content_profile = ContentProfile.objects.get(pk=id)
        if content_profile.created_by == request.user:
            content_profile.delete()
            return HttpResponseRedirect(reverse('content_profiles_list'))
    except Exception, e:
        raise Http404
    return render_to_response('content_profiles/content_profile_drop.html')

def pcu_view(request, pcu_id):
    print "Viewing PCU %s" % pcu_id
    
    pcu = PCU.objects.get(pk = pcu_id)
    
    analyticsRaw = PCUAnalytics.objects.filter(pcu = pcu)
    graphData = generate_stats(analyticsRaw)
    
    return render_to_response('pcu/pcu_view.html', {
        'pcu': pcu,
        'pstats': graphData if graphData else None
    })