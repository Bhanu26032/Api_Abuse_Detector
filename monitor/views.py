from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import APILog
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.timezone import localtime
from django.db.models import Count
from django.template.loader import render_to_string
from django.http import JsonResponse
from .models import APILog

EXCLUDED_PATHS = ['/dashboard/', '/logs/', '/settings/', '/favicon.ico', '/static/']


import httpx
from django.http import JsonResponse

FASTAPI_URL = "http://127.0.0.1:8143"

def proxy_to_fastapi(request, path=''):
    url = f"{FASTAPI_URL}/{path}"
    
    try:
        # Forward method and parameters
        if request.method == 'GET':
            r = httpx.get(url, params=request.GET)
        elif request.method == 'POST':
            r = httpx.post(url, data=request.POST)
        else:
            return JsonResponse({"error": "Unsupported method"}, status=405)
        
        return JsonResponse(r.json(), status=r.status_code)
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
def is_admin(user):
    return user.is_superuser

def home_view(request):
    return render(request, 'monitor/home.html')

@login_required


def logs_view(request):
    logs = APILog.objects.all().order_by('-timestamp')[:100]
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('monitor/log_rows.html', {'logs': logs})
        return JsonResponse({'html': html})
    
    return render(request, 'monitor/logs.html', {'logs': logs})


from django.http import JsonResponse

@login_required
def dashboard_view(request):
    method_counts = list(APILog.objects.values('method').annotate(count=Count('method')))
    ip_counts = list(APILog.objects.values('ip_address','port').annotate(count=Count('ip_address')))

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'methods': method_counts,
            'ips': ip_counts
        })

    return render(request, 'monitor/dashboard.html', {
        'method_data': method_counts,
        'ip_data': ip_counts
    })

@user_passes_test(is_admin)
def settings_view(request):
    user_count = User.objects.count()
    return render(request, 'monitor/settings.html', {'user_count': user_count})




def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if not User.objects.filter(username=username).exists():
            User.objects.create_user(username=username, password=password)
            return redirect('login')
    return render(request, 'monitor/register.html')

def login_view(request):
    if request.method == 'POST':
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user:
            login(request, user)
            return redirect('dashboard')
    return render(request, 'monitor/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def sso_login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        user, created = User.objects.get_or_create(username=username)
        login(request, user)
        return redirect('dashboard')
    return render(request, 'monitor/sso_login.html')
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

@login_required
def settings_view(request):
    if request.user.is_superuser:
        users = User.objects.all()
        return render(request, 'monitor/settings.html', {'users': users})
    else:
        return HttpResponseForbidden("⛔ You are not authorized to access this page.")
