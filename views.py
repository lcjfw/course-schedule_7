import json
from pathlib import Path
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.db.models import F
from .models import Schedule
from .validation import validate
DEFAULT=json.loads((Path(__file__).parent/'default_schedule.json').read_text(encoding='utf-8'))
def record(request):
    return Schedule.objects.get_or_create(user=request.user,defaults={'browser_key':f'user:{request.user.pk}','state':DEFAULT})[0]

def attach_legacy(request, user):
    # Claim only this browser's pre-login timetable; existing account data wins.
    key=request.session.session_key
    if key and not Schedule.objects.filter(user=user).exists():
        Schedule.objects.filter(browser_key=key,user__isnull=True).update(user=user)

def signin(request):
    if request.user.is_authenticated:return redirect('pages:cla')
    form=AuthenticationForm(request,data=request.POST or None)
    if request.method=='POST' and form.is_valid():
        user=form.get_user()
        attach_legacy(request,user)
        login(request,user)
        return redirect('pages:cla')
    return render(request,'pages/auth.html',{'form':form,'signup':False})

def signup(request):
    if request.user.is_authenticated:return redirect('pages:cla')
    form=UserCreationForm(request.POST or None)
    if request.method=='POST' and form.is_valid():
        user=form.save()
        attach_legacy(request,user)
        login(request,user)
        return redirect('pages:cla')
    return render(request,'pages/auth.html',{'form':form,'signup':True})

@require_http_methods(['POST'])
def signout(request):
    logout(request)
    return redirect('pages:login')

@login_required
@ensure_csrf_cookie
def cla(request):
    obj=record(request)
    return render(request,'pages/cla.html',{'initial':{'state':obj.state,'revision':obj.revision}})
@login_required
def courses(request):return render(request,'pages/courses.html')
@login_required
def focus(request):return render(request,'pages/focus.html')
@require_http_methods(['GET','POST'])
def api(request):
    if not request.user.is_authenticated:
        return JsonResponse({"error":"登入已失效，請重新登入後再試。"},status=401)
    obj=record(request)
    if request.method=='GET':return JsonResponse({'state':obj.state,'revision':obj.revision})
    try:
        if len(request.body)>2*1024*1024:raise ValueError('資料過大。')
        payload=json.loads(request.body)
        if not isinstance(payload,dict) or type(payload.get('revision'))!=int:raise ValueError('版本格式錯誤。')
        state=validate(payload.get('state'))
    except (ValueError,TypeError,KeyError) as e:return JsonResponse({'error':str(e)},status=400)
    n=Schedule.objects.filter(pk=obj.pk,revision=payload['revision']).update(state=state,revision=F('revision')+1)
    if not n:return JsonResponse({'error':'其他分頁已修改課表，請重新整理後再試。'},status=409)
    return JsonResponse({'revision':payload['revision']+1})
