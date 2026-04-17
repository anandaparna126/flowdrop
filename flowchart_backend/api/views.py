import json
import hashlib
import secrets
import random
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import User, Session, FlowChart, ChartShare, ChartActivity


AVATAR_COLORS = ['#6366f1','#ec4899','#f59e0b','#10b981','#3b82f6','#8b5cf6','#ef4444','#14b8a6']

def hash_password(password):
    print("def hash password")
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token():
    print("generate token")
    return secrets.token_hex(32)

def get_user_from_request(request):
    print("get user from request function ===========")
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        token = request.COOKIES.get('session_token', '')
    try:
        session = Session.objects.get(token=token, is_active=True, expires_at__gt=timezone.now())
        return session.user
    except Session.DoesNotExist:
        return None

def require_auth(fn):
    print("this is requeire auth function")
    def wrapper(request, *args, **kwargs):
        user = get_user_from_request(request)
        if not user:
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        request.current_user = user
        return fn(request, *args, **kwargs)
    wrapper.__name__ = fn.__name__
    return wrapper


@csrf_exempt
@require_http_methods(['POST'])
def register(request):
    print("coming inside register api ")
    data = json.loads(request.body)
    username = data.get('username', '').strip()
    password = data.get('password', '')
    email = data.get('email', '').strip() or None

    if not username or not password:
        return JsonResponse({'error': 'Username and password required'}, status=400)
    if User.objects.filter(username=username).exists():
        return JsonResponse({'error': 'Username already taken'}, status=400)

    user = User.objects.create(
        username=username,
        password_hash=hash_password(password),
        email=email,
        avatar_color=random.choice(AVATAR_COLORS)
    )
    token = generate_token()
    Session.objects.create(token=token, user=user, expires_at=timezone.now() + timedelta(days=30))
    return JsonResponse({'token': token, 'user': {'id': str(user.id), 'username': user.username, 'avatar_color': user.avatar_color}})


@csrf_exempt
@require_http_methods(['POST'])
def login(request):
    print("coming inside login api")
    data = json.loads(request.body)
    username = data.get('username', '')
    password = data.get('password', '')
    try:
        user = User.objects.get(username=username, password_hash=hash_password(password), is_active=True)
    except User.DoesNotExist:
        return JsonResponse({'error': 'Invalid credentials'}, status=401)
    token = generate_token()
    Session.objects.create(token=token, user=user, expires_at=timezone.now() + timedelta(days=30))
    user.last_login = timezone.now()
    user.save()
    return JsonResponse({'token': token, 'user': {'id': str(user.id), 'username': user.username, 'avatar_color': user.avatar_color}})


@csrf_exempt
@require_auth
@require_http_methods(['POST'])
def logout(request):
    print("coming inside logout api")
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    Session.objects.filter(token=token).update(is_active=False)
    return JsonResponse({'message': 'Logged out'})


@csrf_exempt
@require_auth
@require_http_methods(['GET', 'POST'])
def charts(request):
    print("coming inside charts api")
    user = request.current_user
    if request.method == 'GET':
        print("charts api method is get")
        owned = list(FlowChart.objects.filter(owner=user, is_deleted=False).order_by('-updated_at').values(
            'id', 'title', 'created_at', 'updated_at'))
        shared_ids = ChartShare.objects.filter(shared_with=user, is_active=True).values_list('chart_id', flat=True)
        shared = list(FlowChart.objects.filter(id__in=shared_ids, is_deleted=False).order_by('-updated_at').values(
            'id', 'title', 'created_at', 'updated_at'))
        for c in owned:
            c['id'] = str(c['id'])
            c['role'] = 'owner'
        for c in shared:
            c['id'] = str(c['id'])
            c['role'] = 'shared'
        return JsonResponse({'owned': owned, 'shared': shared})

    data = json.loads(request.body)
    chart = FlowChart.objects.create(
        title=data.get('title', 'Untitled Chart'),
        owner=user,
        canvas_data=data.get('canvas_data', {'nodes': [], 'connections': []})
    )
    ChartActivity.objects.create(chart=chart, user=user, action='created', detail=chart.title)
    return JsonResponse({'id': str(chart.id), 'title': chart.title, 'created_at': str(chart.created_at)})


@csrf_exempt
@require_auth
@require_http_methods(['GET', 'PUT', 'DELETE'])
def chart_detail(request, chart_id):
    print("coming inside chart detail api")
    user = request.current_user
    try:
        chart = FlowChart.objects.get(id=chart_id, is_deleted=False)
    except FlowChart.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)

    is_owner = chart.owner == user
    has_share = ChartShare.objects.filter(chart=chart, shared_with=user, is_active=True).exists()
    if not is_owner and not has_share:
        # Check share token
        return JsonResponse({'error': 'Forbidden'}, status=403)

    if request.method == 'GET':
        print("chart detail method is get")
        return JsonResponse({
            'id': str(chart.id),
            'title': chart.title,
            'canvas_data': chart.canvas_data,
            'owner': chart.owner.username,
            'owner_color': chart.owner.avatar_color,
            'created_at': str(chart.created_at),
            'updated_at': str(chart.updated_at),
            'is_owner': is_owner
        })

    if request.method == 'PUT':
        print("chart detail method is put")
        data = json.loads(request.body)
        if 'title' in data:
            chart.title = data['title']
        if 'canvas_data' in data:
            chart.canvas_data = data['canvas_data']
        chart.save()
        ChartActivity.objects.create(chart=chart, user=user, action='updated', detail=chart.title)
        return JsonResponse({'message': 'Saved', 'updated_at': str(chart.updated_at)})

    if request.method == 'DELETE':
        print("chart detail lethod is delete")
        if not is_owner:
            return JsonResponse({'error': 'Only owner can delete'}, status=403)
        chart.is_deleted = True
        chart.save()
        return JsonResponse({'message': 'Deleted'})


@csrf_exempt
@require_auth
@require_http_methods(['POST', 'GET'])
def share_chart(request, chart_id):
    print("coming inside share chart api")
    user = request.current_user
    try:
        chart = FlowChart.objects.get(id=chart_id, owner=user, is_deleted=False)
    except FlowChart.DoesNotExist:
        return JsonResponse({'error': 'Not found or not owner'}, status=404)

    if request.method == 'POST':
        print("share chart api, method is post")
        data = json.loads(request.body)
        share_type = data.get('type', 'link')  # 'link' or 'user'
        permission = data.get('permission', 'edit')

        if share_type == 'link':
            print("share type is link")
            token = generate_token()[:16]
            share = ChartShare.objects.create(
                chart=chart, shared_by=user, share_token=token, permission=permission
            )
            ChartActivity.objects.create(chart=chart, user=user, action='shared', detail=f'link:{permission}')
            return JsonResponse({'share_token': token, 'share_id': str(share.id)})

        elif share_type == 'user':
            print("share type is user")
            target_username = data.get('username', '')
            try:
                target_user = User.objects.get(username=target_username)
            except User.DoesNotExist:
                return JsonResponse({'error': 'User not found'}, status=404)
            share, created = ChartShare.objects.get_or_create(
                chart=chart, shared_with=target_user,
                defaults={'shared_by': user, 'permission': permission}
            )
            if not created:
                share.permission = permission
                share.is_active = True
                share.save()
            ChartActivity.objects.create(chart=chart, user=user, action='shared', detail=f'user:{target_username}')
            return JsonResponse({'message': f'Shared with {target_username}', 'share_id': str(share.id)})

    if request.method == 'GET':
        print("coming inside share chart api, method is get")
        shares = ChartShare.objects.filter(chart=chart, is_active=True)
        result = []
        for s in shares:
            result.append({
                'id': str(s.id),
                'type': 'user' if s.shared_with else 'link',
                'shared_with': s.shared_with.username if s.shared_with else None,
                'share_token': s.share_token,
                'permission': s.permission,
                'shared_at': str(s.shared_at),
                'accessed_count': s.accessed_count
            })
        return JsonResponse({'shares': result})


@require_http_methods(['GET'])
def access_shared(request, share_token):
    print("coming inside access shared api")
    try:
        share = ChartShare.objects.get(share_token=share_token, is_active=True)
    except ChartShare.DoesNotExist:
        return JsonResponse({'error': 'Invalid or expired share link'}, status=404)
    share.accessed_count += 1
    share.last_accessed = timezone.now()
    share.save()
    chart = share.chart
    return JsonResponse({
        'id': str(chart.id),
        'title': chart.title,
        'canvas_data': chart.canvas_data,
        'owner': chart.owner.username,
        'permission': share.permission
    })


@csrf_exempt
@require_auth
@require_http_methods(['GET'])
def search_users(request):
    print("coming inside search users")
    q = request.GET.get('q', '')
    if len(q) < 2:
        return JsonResponse({'users': []})
    users = User.objects.filter(username__icontains=q, is_active=True).exclude(id=request.current_user.id)[:10]
    return JsonResponse({'users': [{'username': u.username, 'avatar_color': u.avatar_color} for u in users]})


@csrf_exempt
@require_auth
@require_http_methods(['GET'])
def me(request):
    print("coming inside me api")
    user = request.current_user
    return JsonResponse({'id': str(user.id), 'username': user.username, 'avatar_color': user.avatar_color})
