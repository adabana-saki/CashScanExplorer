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
        ('remittance_user', 'Remittance User'),
        ('trader', 'Trader'),
    ]

    TRADER_EXPERIENCE_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('professional', 'Professional'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    age = models.IntegerField(null=True, blank=True)
    parent_email = models.EmailField(null=True, blank=True, help_text="Parent's email for students")
    organization = models.CharField(max_length=200, null=True, blank=True, help_text="School or organization name")

    # Trading-specific fields
    trader_experience_level = models.CharField(
        max_length=20,
        choices=TRADER_EXPERIENCE_CHOICES,
        null=True,
        blank=True,
        help_text="Experience level for traders"
    )

    # Teacher-specific fields
    grade_levels_taught = models.JSONField(
        default=list,
        blank=True,
        help_text="List of grade levels this teacher teaches"
    )
    subjects_taught = models.JSONField(
        default=list,
        blank=True,
        help_text="List of subjects this teacher teaches"
    )

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
        # Teacher plans
        ('teacher_free', 'Teacher Free'),
        ('teacher_pro', 'Teacher Pro'),
        ('district', 'District Plan'),
        # Remittance plans
        ('remittance_free', 'Remittance Free'),
        ('remittance_pro', 'Remittance Pro'),
        # Trading plans
        ('trader_free', 'Trader Free'),
        ('trader_pro', 'Trader Pro'),
        ('trader_premium', 'Trader Premium'),
    ]

    BILLING_PERIOD_CHOICES = [
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('one_time', 'One-time'),
    ]

    name = models.CharField(max_length=100)
    plan_type = models.CharField(max_length=30, choices=PLAN_TYPE_CHOICES, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in USD")
    billing_period = models.CharField(max_length=20, choices=BILLING_PERIOD_CHOICES, default='monthly')

    # General limits
    ai_chat_limit = models.IntegerField(help_text="Daily AI chat limit, -1 for unlimited")
    image_recognition_limit = models.IntegerField(help_text="Daily image recognition limit, -1 for unlimited")

    # Teacher-specific limits
    max_students = models.IntegerField(default=1, help_text="Maximum number of students (for classroom/school plans)")
    max_assignments = models.IntegerField(default=0, help_text="Maximum active assignments, -1 for unlimited")
    ai_lesson_plans_limit = models.IntegerField(default=0, help_text="Monthly AI lesson plan generations, -1 for unlimited")
    worksheet_generation_limit = models.IntegerField(default=0, help_text="Monthly worksheet generations, -1 for unlimited")

    # Remittance-specific limits
    max_rate_alerts = models.IntegerField(default=0, help_text="Maximum active rate alerts, -1 for unlimited")
    comparison_history_days = models.IntegerField(default=30, help_text="Days of comparison history, -1 for unlimited")

    # Trading-specific limits
    max_virtual_portfolios = models.IntegerField(default=0, help_text="Maximum virtual portfolios, -1 for unlimited")
    max_open_trades = models.IntegerField(default=0, help_text="Maximum concurrent open trades, -1 for unlimited")
    historical_data_days = models.IntegerField(default=30, help_text="Days of historical data access, -1 for unlimited")

    features = models.JSONField(default=dict, help_text="Additional features as JSON")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        period_display = f"/{self.billing_period}" if self.billing_period != 'one_time' else ''
        return f"{self.name} (${self.price}{period_display})"


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

    # Extended fields for Phase 1
    grade_level = models.IntegerField(null=True, blank=True, help_text="Grade level (1-12)")
    school_year = models.CharField(max_length=20, null=True, blank=True, help_text="e.g., '2024-2025'")
    subject = models.CharField(max_length=100, null=True, blank=True, help_text="e.g., 'Math', 'Economics'")
    meeting_schedule = models.JSONField(default=dict, blank=True, help_text="Meeting days and times")
    performance_metrics = models.JSONField(default=dict, blank=True, help_text="Cached aggregated performance data")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['teacher', 'is_active']),
            models.Index(fields=['school_year', 'grade_level']),
        ]

    def __str__(self):
        return f"{self.name} - {self.teacher.username}"

# ============================================================================
# Phase 1: Teacher-Focused Models
# ============================================================================

class CurriculumStandard(models.Model):
    """Educational curriculum standards mapping"""

    COUNTRY_CHOICES = [
        ('US', 'United States'),
        ('UK', 'United Kingdom'),
        ('JP', 'Japan'),
        ('AU', 'Australia'),
        ('CA', 'Canada'),
        ('SG', 'Singapore'),
        ('OTHER', 'Other'),
    ]

    country = models.CharField(max_length=10, choices=COUNTRY_CHOICES)
    framework = models.CharField(max_length=100, help_text="e.g., 'Common Core', 'National Curriculum'")
    grade_level = models.IntegerField(help_text="Grade level (1-12)")
    subject = models.CharField(max_length=100, help_text="e.g., 'Math', 'Social Studies'")
    standard_code = models.CharField(max_length=100, help_text="e.g., 'CCSS.MATH.4.MD.A.2'")
    description = models.TextField()
    related_currencies = models.JSONField(default=list, blank=True, help_text="Applicable currency codes")
    parent_standard = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sub_standards',
        help_text="For hierarchical standards"
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['country', 'grade_level', 'subject']),
            models.Index(fields=['standard_code']),
        ]
        unique_together = ['country', 'framework', 'standard_code']

    def __str__(self):
        return f"{self.standard_code} - {self.country} Grade {self.grade_level}"


class Assignment(models.Model):
    """Teacher-created assignments"""

    ASSIGNMENT_TYPE_CHOICES = [
        ('quiz', 'Quiz'),
        ('worksheet', 'Worksheet'),
        ('project', 'Project'),
        ('custom', 'Custom'),
    ]

    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]

    classroom = models.ForeignKey(ClassroomGroup, on_delete=models.CASCADE, related_name='assignments')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_assignments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    assignment_type = models.CharField(max_length=20, choices=ASSIGNMENT_TYPE_CHOICES)
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='medium')
    target_grade = models.IntegerField(help_text="Target grade level (1-12)")

    curriculum_standards = models.ManyToManyField(
        CurriculumStandard,
        related_name='assignments',
        blank=True,
        help_text="Related curriculum standards"
    )

    due_date = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=False, help_text="Visible to students")
    max_points = models.IntegerField(default=100)
    instructions = models.TextField(blank=True)
    time_limit_minutes = models.IntegerField(null=True, blank=True, help_text="Time limit in minutes")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['classroom', 'is_published']),
            models.Index(fields=['teacher', 'created_at']),
            models.Index(fields=['due_date']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.classroom.name}"


class AssignmentQuestion(models.Model):
    """Individual questions within an assignment"""

    QUESTION_TYPE_CHOICES = [
        ('multiple_choice', 'Multiple Choice'),
        ('calculation', 'Calculation'),
        ('conversion', 'Currency Conversion'),
        ('explanation', 'Written Explanation'),
        ('true_false', 'True/False'),
    ]

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='questions')
    question_order = models.IntegerField(default=0, help_text="Display order")
    question_type = models.CharField(max_length=30, choices=QUESTION_TYPE_CHOICES)
    question_text = models.TextField()
    correct_answer = models.TextField()
    answer_options = models.JSONField(default=list, blank=True, help_text="For multiple choice questions")
    points = models.IntegerField(default=10)
    hints = models.JSONField(default=list, blank=True, help_text="List of hints")
    explanation = models.TextField(blank=True, help_text="Explanation of correct answer")
    currencies_involved = models.JSONField(default=list, blank=True, help_text="e.g., ['JPY', 'USD']")

    class Meta:
        ordering = ['assignment', 'question_order']
        indexes = [
            models.Index(fields=['assignment', 'question_order']),
        ]

    def __str__(self):
        return f"{self.assignment.title} - Q{self.question_order}"


class StudentSubmission(models.Model):
    """Student submission for an assignment"""

    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('submitted', 'Submitted'),
        ('graded', 'Graded'),
    ]

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')

    submitted_at = models.DateTimeField(null=True, blank=True)
    total_score = models.IntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True, help_text="Teacher's overall feedback")
    graded_at = models.DateTimeField(null=True, blank=True)
    graded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='graded_submissions'
    )
    time_spent_seconds = models.IntegerField(default=0, help_text="Total time spent in seconds")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['assignment', 'student']
        indexes = [
            models.Index(fields=['assignment', 'status']),
            models.Index(fields=['student', 'submitted_at']),
        ]
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.student.username} - {self.assignment.title} ({self.status})"


class StudentAnswer(models.Model):
    """Individual student answers to assignment questions"""

    submission = models.ForeignKey(StudentSubmission, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(AssignmentQuestion, on_delete=models.CASCADE, related_name='student_answers')
    answer_text = models.TextField()
    is_correct = models.BooleanField(null=True, blank=True, help_text="Set when graded")
    points_earned = models.IntegerField(default=0)
    teacher_comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['submission', 'question']
        indexes = [
            models.Index(fields=['submission', 'question']),
        ]

    def __str__(self):
        return f"{self.submission.student.username} - {self.question}"


class LessonPlan(models.Model):
    """AI-generated or manual lesson plans"""

    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_plans')
    title = models.CharField(max_length=200)
    description = models.TextField()
    grade_level = models.IntegerField(help_text="Target grade level (1-12)")
    duration_minutes = models.IntegerField(help_text="Expected lesson duration")

    curriculum_standards = models.ManyToManyField(
        CurriculumStandard,
        related_name='lesson_plans',
        blank=True
    )

    learning_objectives = models.JSONField(default=list, help_text="List of learning objectives")
    materials_needed = models.JSONField(default=list, help_text="Required materials")
    activity_sequence = models.JSONField(default=list, help_text="Step-by-step activities")
    assessment_methods = models.JSONField(default=list, help_text="How to assess learning")
    currencies_covered = models.JSONField(default=list, help_text="Currency codes covered in lesson")

    ai_generated = models.BooleanField(default=False, help_text="Was this generated by AI")
    template_used = models.CharField(max_length=100, null=True, blank=True)
    is_public = models.BooleanField(default=False, help_text="Share with other teachers")
    downloads_count = models.IntegerField(default=0)
    rating_average = models.FloatField(default=0.0)
    rating_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['teacher', 'created_at']),
            models.Index(fields=['grade_level', 'is_public']),
            models.Index(fields=['-rating_average', '-downloads_count']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - Grade {self.grade_level}"


class Worksheet(models.Model):
    """Printable worksheets"""

    WORKSHEET_TYPE_CHOICES = [
        ('practice', 'Practice'),
        ('assessment', 'Assessment'),
        ('homework', 'Homework'),
        ('activity', 'Activity'),
    ]

    lesson_plan = models.ForeignKey(
        LessonPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='worksheets'
    )
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='worksheets')
    title = models.CharField(max_length=200)
    description = models.TextField()
    worksheet_type = models.CharField(max_length=20, choices=WORKSHEET_TYPE_CHOICES)
    grade_level = models.IntegerField(help_text="Target grade level (1-12)")

    content = models.TextField(help_text="Worksheet content (markdown or HTML)")
    answer_key = models.TextField(blank=True)
    pdf_file = models.FileField(upload_to='worksheets/', null=True, blank=True)

    download_count = models.IntegerField(default=0)
    is_public = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['teacher', 'created_at']),
            models.Index(fields=['grade_level', 'worksheet_type']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.worksheet_type}"


class TeacherResource(models.Model):
    """Shared teaching resources"""

    RESOURCE_TYPE_CHOICES = [
        ('lesson_plan', 'Lesson Plan'),
        ('worksheet', 'Worksheet'),
        ('activity', 'Activity'),
        ('video', 'Video'),
        ('link', 'External Link'),
        ('presentation', 'Presentation'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPE_CHOICES)

    file = models.FileField(upload_to='teacher_resources/', null=True, blank=True)
    external_url = models.URLField(null=True, blank=True)

    grade_levels = models.JSONField(default=list, help_text="Applicable grade levels")
    subjects = models.JSONField(default=list, help_text="Applicable subjects")

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_resources')
    is_free = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0, help_text="Price in USD")

    downloads = models.IntegerField(default=0)
    rating = models.FloatField(default=0.0)
    rating_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['resource_type', '-downloads']),
            models.Index(fields=['-rating', '-downloads']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.resource_type})"
