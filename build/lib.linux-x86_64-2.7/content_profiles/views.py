# Create your views here.
from datetime import datetime, timedelta
from django.conf import settings
from api import ACTION_TYPES
from api.models import Action
from content_profiles.forms import ContentProfileAddForm
from content_profiles.models import ContentProfile
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db.models.aggregates import Count, Sum
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
import logging

@login_required()
def content_profile_list(request):
    content_profiles_full = ContentProfile.objects.filter(created_by = request.user)
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
            new_profile.save()
            return HttpResponseRedirect(reverse('content_profiles_list'))

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
    try:
        content_profile = ContentProfile.objects.get(pk = id)
        daysago6 = datetime.today() - timedelta(days=6)
        stats = Action.objects.filter(profile=content_profile.pk, action_datetime__gte=daysago6,action_datetime__lte=datetime.today()).extra({'action_datetime' : "date(action_datetime)"}).values('action_datetime').annotate(seen=Sum('is_seen'),read=Sum('is_read')).order_by('action_datetime')
        pstats = list()
        curdate = daysago6
        if stats:
            for stat in stats:
                gapsize = (datetime.strptime(stat['action_datetime'],'%Y-%m-%d')-curdate).days
                if gapsize > 0:
                    dategap = [curdate + timedelta(days=x) for x in range(0,gapsize+1)]
                    for dg in [datetime.strftime(x,'%b %d') for x in dategap]:
                        pstats.append({'action_datetime':dg, 'seen':0, 'read':0})

                rectime = datetime.strptime(stat['action_datetime'],'%Y-%m-%d')
                rectimestr = datetime.strftime(rectime, '%b %d')
                pstats.append({'action_datetime':rectimestr, 'seen':stat['seen'], 'read':stat['read']})
                curdate = datetime.strptime(stat['action_datetime'],'%Y-%m-%d') + timedelta(days=1)

            gapsize = (datetime.today()-curdate).days
            if gapsize > 0:
                dategap = [curdate + timedelta(days=x) for x in range(0,gapsize+1)]
                for dg in [datetime.strftime(x,'%b %d') for x in dategap]:
                    pstats.append({'action_datetime':dg, 'seen':0, 'read':0})
        else:
            gapsize = (datetime.today() - daysago6).days
            if gapsize > 0:
                dategap = [curdate + timedelta(days=x) for x in range(0,gapsize+1)]
                for dg in [datetime.strftime(x,'%b %d') for x in dategap]:
                    pstats.append({'action_datetime':dg, 'seen':0, 'read':0})

    except Exception, e:
        raise Http404


    request.breadcrumbs([
        ("Profiles", reverse('content_profiles_list')),
        (content_profile.name, ''),
    ])

    return render_to_response('content_profiles/content_profile_view.html',
        {
            'content_profile': content_profile,
            'pstats': pstats
            },
        context_instance=RequestContext(request))

@login_required()
def content_profile_drop(request, id):
    try:
        content_profile = ContentProfile.objects.get(pk = id)
        if content_profile.created_by == request.user:
            content_profile.delete()
            return HttpResponseRedirect(reverse('content_profiles_list'))
    except Exception, e:
        raise Http404
    return render_to_response('content_profiles/content_profile_drop.html')
