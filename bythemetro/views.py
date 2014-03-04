from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.template import RequestContext

from bythemetro.models import *
from bythemetro.forms import RegistrationForm, ApartmentAlertForm

def main_page(request):
    metro_system = MetroSystem.objects.get(pk=1)
    vars = RequestContext(request, {'metro_system': metro_system})
    return render_to_response('map.html', vars)

def map(request):
    metro_system = MetroSystem.objects.get(pk=1)
    vars = RequestContext(request, {'metro_system': metro_system})
    return render_to_response('map.html', vars)

def table(request):
    metro_system = MetroSystem.objects.get(pk=1)
    vars = RequestContext(request, {'metro_system': metro_system})
    return render_to_response('table.html', vars)

def logout_page(request):
    logout(request)
    return HttpResponseRedirect('/')

@login_required
def user_page(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    vars = RequestContext(request)
    return render_to_response('user.html', vars)

def alerts(request):
    """
    Display a list of alerts that the user has configured. Or if the
    user has not logged in, then the template will display a message
    indicating that the user must login before configuring any alerts.
    """
    vars = RequestContext(request)
    if request.user.is_authenticated():
        user = get_object_or_404(User, pk=request.user.id)
        vars.update({'alert_list': user.apartmentalert_set.all()})
    return render_to_response('alerts/index.html', vars)
    
@login_required
def alert_detail(request, alert_id):
    alert = get_object_or_404(ApartmentAlert, pk=alert_id)
    vars = RequestContext(request, {'alert': alert})
    return render_to_response('alerts/detail.html', vars)
    
def register_page(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username = form.cleaned_data['username'],
                password = form.cleaned_data['password1'],
                email = form.cleaned_data['email']
            )
            return HttpResponseRedirect('/')
    else:
        form = RegistrationForm()

    vars = RequestContext(request, {'form': form})
    return render_to_response('registration/register.html', vars)

def create_alert(request):
    if request.method == 'POST':
        form = ApartmentAlertForm(request.POST)
        if form.is_valid():
            alert = form.save(commit=False)
            alert.user = request.user
            alert.save()
            return HttpResponseRedirect('/alerts/')
    else:
        form = ApartmentAlertForm()

    vars = RequestContext(request, {'form': form})
    return render_to_response('alerts/create.html', vars)

def edit_alert(request, alert_id):
    alert = get_object_or_404(ApartmentAlert, pk=alert_id)
        
    if request.method == 'POST':
        form = ApartmentAlertForm(request.POST, instance=alert)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/alerts/')
    else:
        form = ApartmentAlertForm(instance=alert)

    vars = RequestContext(request, {'form': form})
    return render_to_response('alerts/edit.html', vars)

def delete_alert(request, alert_id):
    alert = get_object_or_404(ApartmentAlert, pk=alert_id)
        
    if request.method == 'POST':
        print request.POST
        alert.delete()
        return HttpResponseRedirect('/alerts/')

    vars = RequestContext(request, {'alert': alert})
    return render_to_response('alerts/delete.html', vars)


