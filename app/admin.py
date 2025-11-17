from django.contrib import admin
from .models import (
    ExchangeRate, UserProfile, SubscriptionPlan, Subscription,
    UsageStatistics, LearningProgress, Achievement, UserAchievement,
    ClassroomGroup
)


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ['currency_pair', 'date', 'rate', 'created_at']
    list_filter = ['currency_pair', 'date']
    search_fields = ['currency_pair']
    ordering = ['-date']


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'age', 'organization', 'created_at']
    list_filter = ['role', 'organization']
    search_fields = ['user__username', 'user__email', 'organization']
    raw_id_fields = ['user']


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan_type', 'price', 'ai_chat_limit', 'image_recognition_limit', 'max_students', 'is_active']
    list_filter = ['plan_type', 'is_active']
    search_fields = ['name', 'plan_type']
    ordering = ['price']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'status', 'current_period_start', 'current_period_end', 'created_at']
    list_filter = ['status', 'plan']
    search_fields = ['user__username', 'user__email', 'stripe_customer_id']
    raw_id_fields = ['user', 'plan']
    readonly_fields = ['stripe_customer_id', 'stripe_subscription_id', 'created_at', 'updated_at']


@admin.register(UsageStatistics)
class UsageStatisticsAdmin(admin.ModelAdmin):
    list_display = ['user', 'feature', 'count', 'date', 'updated_at']
    list_filter = ['feature', 'date']
    search_fields = ['user__username']
    raw_id_fields = ['user']
    ordering = ['-date', '-count']


@admin.register(LearningProgress)
class LearningProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'points_earned', 'timestamp']
    list_filter = ['activity_type', 'timestamp']
    search_fields = ['user__username']
    raw_id_fields = ['user']
    ordering = ['-timestamp']


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['name', 'points_required', 'activity_count_required', 'activity_type', 'is_active']
    list_filter = ['is_active', 'activity_type']
    search_fields = ['name', 'description']
    ordering = ['points_required']


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ['user', 'achievement', 'earned_at']
    list_filter = ['achievement', 'earned_at']
    search_fields = ['user__username', 'achievement__name']
    raw_id_fields = ['user', 'achievement']
    ordering = ['-earned_at']


@admin.register(ClassroomGroup)
class ClassroomGroupAdmin(admin.ModelAdmin):
    list_display = ['name', 'teacher', 'access_code', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'teacher__username', 'access_code']
    raw_id_fields = ['teacher']
    filter_horizontal = ['students']
    ordering = ['-created_at']
