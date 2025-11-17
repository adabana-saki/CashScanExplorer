from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime, timedelta

class ExchangeRate(models.Model):
    date = models.DateField()
    rate = models.FloatField()
    currency_pair = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        get_latest_by = 'date'

    def __str__(self):
        return f"{self.currency_pair} - {self.date}: {self.rate}"


class UserProfile(models.Model):
    """Extended user profile with role and subscription information"""

    ROLE_CHOICES = [
        ('student', 'Student'),
        ('parent', 'Parent'),
        ('teacher', 'Teacher'),
        ('admin', 'Administrator'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    age = models.IntegerField(null=True, blank=True)
    parent_email = models.EmailField(null=True, blank=True, help_text="Parent's email for students")
    organization = models.CharField(max_length=200, null=True, blank=True, help_text="School or organization name")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"


class SubscriptionPlan(models.Model):
    """Define available subscription plans"""

    PLAN_TYPE_CHOICES = [
        ('free', 'Free Plan'),
        ('premium', 'Premium Plan'),
        ('classroom', 'Classroom Plan'),
        ('school', 'School Plan'),
    ]

    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPE_CHOICES, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Monthly price in USD")
    ai_chat_limit = models.IntegerField(help_text="Daily AI chat limit, -1 for unlimited")
    image_recognition_limit = models.IntegerField(help_text="Daily image recognition limit, -1 for unlimited")
    max_students = models.IntegerField(default=1, help_text="Maximum number of students (for classroom/school plans)")
    features = models.JSONField(default=dict, help_text="Additional features as JSON")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (${self.price}/month)"


class Subscription(models.Model):
    """User subscription details"""

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
        ('trial', 'Trial'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    stripe_customer_id = models.CharField(max_length=255, null=True, blank=True)
    stripe_subscription_id = models.CharField(max_length=255, null=True, blank=True)
    current_period_start = models.DateTimeField(default=timezone.now)
    current_period_end = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_valid(self):
        """Check if subscription is currently valid"""
        if self.status not in ['active', 'trial']:
            return False
        if self.current_period_end and self.current_period_end < timezone.now():
            return False
        return True

    def __str__(self):
        return f"{self.user.username} - {self.plan.name} ({self.status})"


class UsageStatistics(models.Model):
    """Track daily usage for rate limiting"""

    FEATURE_CHOICES = [
        ('ai_chat', 'AI Chat'),
        ('image_recognition', 'Image Recognition'),
        ('currency_conversion', 'Currency Conversion'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='usage_stats')
    feature = models.CharField(max_length=30, choices=FEATURE_CHOICES)
    count = models.IntegerField(default=0)
    date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'feature', 'date']
        ordering = ['-date']

    @staticmethod
    def get_today_usage(user, feature):
        """Get today's usage count for a specific feature"""
        today = timezone.now().date()
        stat, created = UsageStatistics.objects.get_or_create(
            user=user,
            feature=feature,
            date=today,
            defaults={'count': 0}
        )
        return stat.count

    @staticmethod
    def increment_usage(user, feature):
        """Increment usage count for today"""
        today = timezone.now().date()
        stat, created = UsageStatistics.objects.get_or_create(
            user=user,
            feature=feature,
            date=today,
            defaults={'count': 0}
        )
        stat.count += 1
        stat.save()
        return stat.count

    def __str__(self):
        return f"{self.user.username} - {self.feature} - {self.date}: {self.count}"


class LearningProgress(models.Model):
    """Track student learning progress and achievements"""

    ACTIVITY_CHOICES = [
        ('currency_learned', 'Currency Learned'),
        ('exchange_rate_checked', 'Exchange Rate Checked'),
        ('ai_chat_completed', 'AI Chat Completed'),
        ('image_recognized', 'Image Recognized'),
        ('quiz_completed', 'Quiz Completed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_progress')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_CHOICES)
    details = models.JSONField(default=dict, help_text="Additional details about the activity")
    points_earned = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user.username} - {self.activity_type} - {self.timestamp}"


class Achievement(models.Model):
    """Gamification: Badges and achievements"""

    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="Icon identifier or emoji")
    points_required = models.IntegerField(default=0)
    activity_count_required = models.IntegerField(default=0, help_text="Number of activities required")
    activity_type = models.CharField(max_length=50, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    """Track user achievements"""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'achievement']
        ordering = ['-earned_at']

    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"


class ClassroomGroup(models.Model):
    """For teachers to manage groups of students"""

    name = models.CharField(max_length=200)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teaching_groups')
    students = models.ManyToManyField(User, related_name='student_groups', blank=True)
    description = models.TextField(null=True, blank=True)
    access_code = models.CharField(max_length=20, unique=True, help_text="Code for students to join")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} - {self.teacher.username}"