from django.db import models
import uuid


class User(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=100, unique=True)
    password_hash = models.CharField(max_length=256)
    email = models.EmailField(unique=True, blank=True, null=True)
    avatar_color = models.CharField(max_length=7, default='#6366f1')
    created_at = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)


class Session(models.Model):
    token = models.CharField(max_length=256, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)


class FlowChart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, default='Untitled Chart')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_charts')
    canvas_data = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)


class ChartShare(models.Model):
    PERMISSION_CHOICES = [('view', 'View'), ('edit', 'Edit')]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chart = models.ForeignKey(FlowChart, on_delete=models.CASCADE, related_name='shares')
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shares_given')
    shared_with = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shares_received', null=True, blank=True)
    share_token = models.CharField(max_length=64, unique=True, null=True, blank=True)
    permission = models.CharField(max_length=10, choices=PERMISSION_CHOICES, default='edit')
    shared_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    accessed_count = models.IntegerField(default=0)
    last_accessed = models.DateTimeField(null=True, blank=True)


class ChartActivity(models.Model):
    chart = models.ForeignKey(FlowChart, on_delete=models.CASCADE, related_name='activities')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=50)
    detail = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
