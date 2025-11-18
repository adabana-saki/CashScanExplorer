from django.contrib import admin
from .models import (
    ExchangeRate, UserProfile, SubscriptionPlan, Subscription,
    UsageStatistics, LearningProgress, Achievement, UserAchievement,
    ClassroomGroup, CurriculumStandard, Assignment, AssignmentQuestion,
    StudentSubmission, StudentAnswer, LessonPlan, Worksheet, TeacherResource
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
    list_display = ['name', 'teacher', 'grade_level', 'subject', 'school_year', 'access_code', 'is_active', 'created_at']
    list_filter = ['is_active', 'grade_level', 'subject', 'school_year', 'created_at']
    search_fields = ['name', 'teacher__username', 'access_code', 'subject']
    raw_id_fields = ['teacher']
    filter_horizontal = ['students']
    ordering = ['-created_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'teacher', 'description', 'access_code')
        }),
        ('Academic Details', {
            'fields': ('grade_level', 'school_year', 'subject', 'meeting_schedule')
        }),
        ('Students', {
            'fields': ('students',)
        }),
        ('Status & Metrics', {
            'fields': ('is_active', 'performance_metrics')
        }),
    )

# ============================================================================
# Phase 1: Teacher-Focused Models Admin
# ============================================================================

@admin.register(CurriculumStandard)
class CurriculumStandardAdmin(admin.ModelAdmin):
    list_display = ['standard_code', 'country', 'grade_level', 'subject', 'framework', 'is_active']
    list_filter = ['country', 'grade_level', 'subject', 'is_active', 'framework']
    search_fields = ['standard_code', 'description', 'framework']
    raw_id_fields = ['parent_standard']
    ordering = ['country', 'grade_level', 'subject', 'standard_code']
    fieldsets = (
        ('Identification', {
            'fields': ('country', 'framework', 'standard_code')
        }),
        ('Content', {
            'fields': ('grade_level', 'subject', 'description', 'related_currencies')
        }),
        ('Hierarchy', {
            'fields': ('parent_standard',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


class AssignmentQuestionInline(admin.TabularInline):
    model = AssignmentQuestion
    extra = 1
    fields = ['question_order', 'question_type', 'question_text', 'correct_answer', 'points']
    ordering = ['question_order']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'classroom', 'teacher', 'assignment_type', 'difficulty', 'target_grade', 'is_published', 'due_date', 'created_at']
    list_filter = ['assignment_type', 'difficulty', 'target_grade', 'is_published', 'created_at']
    search_fields = ['title', 'description', 'teacher__username', 'classroom__name']
    raw_id_fields = ['classroom', 'teacher']
    filter_horizontal = ['curriculum_standards']
    inlines = [AssignmentQuestionInline]
    ordering = ['-created_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'classroom', 'teacher')
        }),
        ('Assignment Details', {
            'fields': ('assignment_type', 'difficulty', 'target_grade', 'max_points', 'time_limit_minutes')
        }),
        ('Instructions', {
            'fields': ('instructions',)
        }),
        ('Curriculum Alignment', {
            'fields': ('curriculum_standards',)
        }),
        ('Publication', {
            'fields': ('is_published', 'due_date')
        }),
    )


@admin.register(AssignmentQuestion)
class AssignmentQuestionAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'question_order', 'question_type', 'points']
    list_filter = ['question_type', 'assignment__assignment_type']
    search_fields = ['question_text', 'assignment__title']
    raw_id_fields = ['assignment']
    ordering = ['assignment', 'question_order']


class StudentAnswerInline(admin.TabularInline):
    model = StudentAnswer
    extra = 0
    fields = ['question', 'answer_text', 'is_correct', 'points_earned', 'teacher_comment']
    readonly_fields = ['question', 'answer_text']


@admin.register(StudentSubmission)
class StudentSubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'assignment', 'status', 'total_score', 'submitted_at', 'graded_at']
    list_filter = ['status', 'submitted_at', 'graded_at']
    search_fields = ['student__username', 'assignment__title']
    raw_id_fields = ['assignment', 'student', 'graded_by']
    inlines = [StudentAnswerInline]
    ordering = ['-submitted_at']
    readonly_fields = ['created_at', 'updated_at', 'time_spent_seconds']
    fieldsets = (
        ('Submission Info', {
            'fields': ('assignment', 'student', 'status')
        }),
        ('Timing', {
            'fields': ('submitted_at', 'time_spent_seconds', 'created_at', 'updated_at')
        }),
        ('Grading', {
            'fields': ('total_score', 'graded_at', 'graded_by', 'feedback')
        }),
    )


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ['submission', 'question', 'is_correct', 'points_earned']
    list_filter = ['is_correct', 'created_at']
    search_fields = ['submission__student__username', 'question__question_text']
    raw_id_fields = ['submission', 'question']
    ordering = ['-created_at']


@admin.register(LessonPlan)
class LessonPlanAdmin(admin.ModelAdmin):
    list_display = ['title', 'teacher', 'grade_level', 'duration_minutes', 'ai_generated', 'is_public', 'downloads_count', 'rating_average', 'created_at']
    list_filter = ['grade_level', 'ai_generated', 'is_public', 'created_at']
    search_fields = ['title', 'description', 'teacher__username']
    raw_id_fields = ['teacher']
    filter_horizontal = ['curriculum_standards']
    ordering = ['-created_at']
    readonly_fields = ['downloads_count', 'rating_average', 'rating_count', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'teacher', 'grade_level', 'duration_minutes')
        }),
        ('Lesson Content', {
            'fields': ('learning_objectives', 'materials_needed', 'activity_sequence', 'assessment_methods', 'currencies_covered')
        }),
        ('Curriculum Alignment', {
            'fields': ('curriculum_standards',)
        }),
        ('Generation Info', {
            'fields': ('ai_generated', 'template_used')
        }),
        ('Sharing', {
            'fields': ('is_public', 'downloads_count', 'rating_average', 'rating_count')
        }),
    )


@admin.register(Worksheet)
class WorksheetAdmin(admin.ModelAdmin):
    list_display = ['title', 'teacher', 'worksheet_type', 'grade_level', 'is_public', 'download_count', 'created_at']
    list_filter = ['worksheet_type', 'grade_level', 'is_public', 'created_at']
    search_fields = ['title', 'description', 'teacher__username']
    raw_id_fields = ['teacher', 'lesson_plan']
    ordering = ['-created_at']
    readonly_fields = ['download_count', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'teacher', 'lesson_plan')
        }),
        ('Worksheet Details', {
            'fields': ('worksheet_type', 'grade_level', 'content', 'answer_key', 'pdf_file')
        }),
        ('Sharing', {
            'fields': ('is_public', 'download_count')
        }),
    )


@admin.register(TeacherResource)
class TeacherResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'resource_type', 'created_by', 'is_free', 'price', 'downloads', 'rating', 'created_at']
    list_filter = ['resource_type', 'is_free', 'created_at']
    search_fields = ['title', 'description', 'created_by__username']
    raw_id_fields = ['created_by']
    ordering = ['-created_at']
    readonly_fields = ['downloads', 'rating', 'rating_count', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'resource_type', 'created_by')
        }),
        ('Content', {
            'fields': ('file', 'external_url')
        }),
        ('Classification', {
            'fields': ('grade_levels', 'subjects')
        }),
        ('Pricing', {
            'fields': ('is_free', 'price')
        }),
        ('Metrics', {
            'fields': ('downloads', 'rating', 'rating_count')
        }),
    )
