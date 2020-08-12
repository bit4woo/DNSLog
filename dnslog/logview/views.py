# coding=utf-8

from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.core.paginator import (
    Paginator, InvalidPage, EmptyPage, PageNotAnInteger)
from django import forms
from models import *
from dnslog import settings
from django.contrib.auth import logout
import json
import hashlib
import time


def index(request):
    http_host = request.get_host()
    if ":" in http_host:
        http_host = http_host.split(':')[0]

    headerList = []
    for item in request.META:
        if item.startswith("HTTP_"):
            headerList.append("{0}: {1}".format(item, request.META[item]))
    http_user_agent = "\r\n".join(headerList) or ' '

    remote_addr = request.META.get(
        'HTTP_X_REAL_IP') or request.META.get('REMOTE_ADDR')
    path = http_host + request.get_full_path()
    if http_host == settings.ADMIN_DOMAIN:
        return login(request)
    elif http_host.endswith(settings.DNS_DOMAIN):
        # httplog 记录处理流程
        subdomain = http_host.replace(settings.DNS_DOMAIN, '')
        if subdomain:
            domains = subdomain.split('.')
            udomain = ''
            if len(domains) >= 2:
                udomain = domains[-2]
                user = User.objects.filter(udomain__exact=udomain)
                if user:
                    weblog = WebLog(
                        user=user[0], path=path, remote_addr=remote_addr,
                        http_user_agent=http_user_agent)
                    weblog.save()
                    return HttpResponse('good boy')
        return HttpResponse('bad boy')

    else:
        return HttpResponse('god is girl')


class UserForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=128)
    password = forms.CharField(label='密  码', widget=forms.PasswordInput())


def login(request):
    userid = request.session.get('userid', None)
    if userid:
        # 已经登陆则直接进入管理页面
        return logview(request, userid)
    if request.method == 'POST':
        uf = UserForm(request.POST)
        if uf.is_valid():
            username = uf.cleaned_data['username']
            password = uf.cleaned_data['password']
            user = User.objects.filter(
                username__exact=username, password__exact=password)
            if user:
                request.session['userid'] = user[0].id
                token = hashlib.md5(username+password+str(time.time())).hexdigest()
                User.objects.filter(username__exact=username).update(token=token)
                return logview(request, user[0].id)
            else:
                return render(
                    request, 'login.html', {
                        'uf': uf,
                        'error': 'username or password error!'
                    })
    else:
        uf = UserForm()
    return render(request, 'login.html', {'uf': uf})


def my_logout(request):
    logout(request)
    return HttpResponseRedirect('/')


def getpage(p):
    try:
        page = int(p)
        if page < 1:
            page = 1
    except ValueError:
        page = 1
    return page


def logview(request, userid):
    user = User.objects.filter(id__exact=userid)[0]
    vardict = {}
    logtype = request.GET.get("logtype", 'dns')
    deltype = request.GET.get("del")
    if deltype == 'dns':
        DNSLog.objects.filter(user=user).delete()
        return HttpResponseRedirect('/?logtype=dns')
    if deltype == 'web':
        WebLog.objects.filter(user=user).delete()
        return HttpResponseRedirect('/?logtype=web')
    if logtype == 'dns':
        vardict['logtype'] = logtype
        dnspage = getpage(request.GET.get("dnspage", 1))
        paginator = Paginator(DNSLog.objects.filter(user=user).order_by('-id'), 10)
        try:
            dnslogs = paginator.page(dnspage)
        except(EmptyPage, InvalidPage, PageNotAnInteger):
            dnspage = paginator.num_pages
            dnslogs = paginator.page(paginator.num_pages)
        vardict['dnspage'] = dnspage
        vardict['pagerange'] = paginator.page_range
        vardict['dnslogs'] = dnslogs
        vardict['numpages'] = paginator.num_pages
    elif logtype == 'web':
        vardict['logtype'] = logtype
        webpage = getpage(request.GET.get("webpage", 1))
        paginator = Paginator(WebLog.objects.filter(user=user).order_by('-id'), 10)
        try:
            weblogs = paginator.page(webpage)
        except(EmptyPage, InvalidPage, PageNotAnInteger):
            webpage = paginator.num_pages
            weblogs = paginator.page(paginator.num_pages)
        vardict['webpage'] = webpage
        vardict['pagerange'] = paginator.page_range
        vardict['weblogs'] = weblogs
        vardict['numpages'] = paginator.num_pages
    else:
        return HttpResponseRedirect('/')

    vardict['userdomain'] = user.udomain + '.' + settings.DNS_DOMAIN

    vardict['udomain'] = str(user.udomain)
    vardict['admindomain'] = str(settings.ADMIN_DOMAIN)

    return render_to_response('views.html', vardict)


def xxxxapilogin(request):
    if request.method =="POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = User.objects.filter(
            username__exact=username, password__exact=password)
        if user:
            request.session['userid'] = user[0].id
            token = hashlib.md5(username + password + str(time.time())).hexdigest()
            User.objects.filter(username__exact=username).update(token=token)
            resp = {'token': token}
            return HttpResponse(json.dumps(resp), content_type="application/json")

def apilogin(request,username,password):#http://127.0.0.1:8000/apilogin/test/123456/
    apistatus = False
    token = ""
    user = User.objects.filter(
        username__exact=username, password__exact=password)
    if user:
        apistatus = True

        request.session['userid'] = user[0].id
        token = hashlib.md5(username + password + str(time.time())).hexdigest()
        User.objects.filter(username__exact=username).update(token=token)
    else:
        pass
    resp = {'status': apistatus, 'token': token}
    return HttpResponse(json.dumps(resp), content_type="application/json")

def apiquery(request,logtype,subdomain,token):#http://127.0.0.1:8000/apiquery/dns/test/a2f78f403d7b8b92ca3486bb4dc0e498/
    apistatus = False
    content = []
    user = User.objects.filter(token__exact=token)
    if user and logtype == 'dns':
        res = DNSLog.objects.filter(host__contains=subdomain)
        if len(res) > 0:
            apistatus = True
            for e in res:
                content.append(e.host)
    elif user and logtype == 'web':
        res = WebLog.objects.filter(path__contains=subdomain)
        if len(res) > 0:
            apistatus = True
            for e in res:
                content.append(e.path)
    else:
       pass
        # return HttpResponseRedirect('/')
    #return render(request, 'api.html', {'content':",".join(content)})
    #不调用模板，直接返回数据
    resp = {'status': apistatus, 'content': ",".join(content)}
    return HttpResponse(json.dumps(resp), content_type="application/json")

def apidel(request,logtype,subdomain,token):#http://127.0.0.1:8000/apidel/dns/test/a2f78f403d7b8b92ca3486bb4dc0e498/
    user = User.objects.filter(token__exact=token)
    apistatus = False #del success or not
    if user and logtype == 'dns':
        DNSLog.objects.filter(user=user,host__contains=subdomain).delete()
        res = DNSLog.objects.filter(host__contains=subdomain)
        if len(res) == 0:
            apistatus = True
    elif user and logtype == 'web':
        WebLog.objects.filter(user=user,host__contains=subdomain).delete()
        res = WebLog.objects.filter(path__contains=subdomain)
        if len(res) == 0:
            apistatus = True
    else:
        pass
        # return HttpResponseRedirect('/')
    resp = {'status': apistatus}
    return HttpResponse(json.dumps(resp), content_type="application/json")
