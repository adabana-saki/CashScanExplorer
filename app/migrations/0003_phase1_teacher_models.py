# Generated migration for Phase 1: Teacher-focused platform models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0002_alter_exchangerate_options'),
    ]

    operations = [
        # Extend UserProfile
        migrations.AddField(
            model_name='userprofile',
            name='trader_experience_level',
            field=models.CharField(
                blank=True,
                choices=[
                    ('beginner', 'Beginner'),
                    ('intermediate', 'Intermediate'),
                    ('advanced', 'Advanced'),
                    ('professional', 'Professional')
                ],
                help_text='Experience level for traders',
                max_length=20,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='grade_levels_taught',
            field=models.JSONField(
                blank=True,
                default=list,
                help_text='List of grade levels this teacher teaches'
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='subjects_taught',
            field=models.JSONField(
                blank=True,
                default=list,
                help_text='List of subjects this teacher teaches'
            ),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='role',
            field=models.CharField(
                choices=[
                    ('student', 'Student'),
                    ('parent', 'Parent'),
                    ('teacher', 'Teacher'),
                    ('admin', 'Administrator'),
                    ('remittance_user', 'Remittance User'),
                    ('trader', 'Trader')
                ],
                default='student',
                max_length=20
            ),
        ),

        # Extend SubscriptionPlan
        migrations.AddField(
            model_name='subscriptionplan',
            name='billing_period',
            field=models.CharField(
                choices=[
                    ('monthly', 'Monthly'),
                    ('yearly', 'Yearly'),
                    ('one_time', 'One-time')
                ],
                default='monthly',
                max_length=20
            ),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='max_assignments',
            field=models.IntegerField(
                default=0,
                help_text='Maximum active assignments, -1 for unlimited'
            ),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='ai_lesson_plans_limit',
            field=models.IntegerField(
                default=0,
                help_text='Monthly AI lesson plan generations, -1 for unlimited'
            ),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='worksheet_generation_limit',
            field=models.IntegerField(
                default=0,
                help_text='Monthly worksheet generations, -1 for unlimited'
            ),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='max_rate_alerts',
            field=models.IntegerField(
                default=0,
                help_text='Maximum active rate alerts, -1 for unlimited'
            ),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='comparison_history_days',
            field=models.IntegerField(
                default=30,
                help_text='Days of comparison history, -1 for unlimited'
            ),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='max_virtual_portfolios',
            field=models.IntegerField(
                default=0,
                help_text='Maximum virtual portfolios, -1 for unlimited'
            ),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='max_open_trades',
            field=models.IntegerField(
                default=0,
                help_text='Maximum concurrent open trades, -1 for unlimited'
            ),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='historical_data_days',
            field=models.IntegerField(
                default=30,
                help_text='Days of historical data access, -1 for unlimited'
            ),
        ),
        migrations.AlterField(
            model_name='subscriptionplan',
            name='plan_type',
            field=models.CharField(
                choices=[
                    ('free', 'Free Plan'),
                    ('premium', 'Premium Plan'),
                    ('classroom', 'Classroom Plan'),
                    ('school', 'School Plan'),
                    ('teacher_free', 'Teacher Free'),
                    ('teacher_pro', 'Teacher Pro'),
                    ('district', 'District Plan'),
                    ('remittance_free', 'Remittance Free'),
                    ('remittance_pro', 'Remittance Pro'),
                    ('trader_free', 'Trader Free'),
                    ('trader_pro', 'Trader Pro'),
                    ('trader_premium', 'Trader Premium')
                ],
                max_length=30,
                unique=True
            ),
        ),

        # Extend ClassroomGroup
        migrations.AddField(
            model_name='classroomgroup',
            name='grade_level',
            field=models.IntegerField(
                blank=True,
                help_text='Grade level (1-12)',
                null=True
            ),
        ),
        migrations.AddField(
            model_name='classroomgroup',
            name='school_year',
            field=models.CharField(
                blank=True,
                help_text="e.g., '2024-2025'",
                max_length=20,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='classroomgroup',
            name='subject',
            field=models.CharField(
                blank=True,
                help_text="e.g., 'Math', 'Economics'",
                max_length=100,
                null=True
            ),
        ),
        migrations.AddField(
            model_name='classroomgroup',
            name='meeting_schedule',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text='Meeting days and times'
            ),
        ),
        migrations.AddField(
            model_name='classroomgroup',
            name='performance_metrics',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text='Cached aggregated performance data'
            ),
        ),

        # Create CurriculumStandard
        migrations.CreateModel(
            name='CurriculumStandard',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(
                    choices=[
                        ('US', 'United States'),
                        ('UK', 'United Kingdom'),
                        ('JP', 'Japan'),
                        ('AU', 'Australia'),
                        ('CA', 'Canada'),
                        ('SG', 'Singapore'),
                        ('OTHER', 'Other')
                    ],
                    max_length=10
                )),
                ('framework', models.CharField(help_text="e.g., 'Common Core', 'National Curriculum'", max_length=100)),
                ('grade_level', models.IntegerField(help_text='Grade level (1-12)')),
                ('subject', models.CharField(help_text="e.g., 'Math', 'Social Studies'", max_length=100)),
                ('standard_code', models.CharField(help_text="e.g., 'CCSS.MATH.4.MD.A.2'", max_length=100)),
                ('description', models.TextField()),
                ('related_currencies', models.JSONField(blank=True, default=list, help_text='Applicable currency codes')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('parent_standard', models.ForeignKey(
                    blank=True,
                    help_text='For hierarchical standards',
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='sub_standards',
                    to='app.curriculumstandard'
                )),
            ],
        ),

        # Create Assignment
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('assignment_type', models.CharField(
                    choices=[
                        ('quiz', 'Quiz'),
                        ('worksheet', 'Worksheet'),
                        ('project', 'Project'),
                        ('custom', 'Custom')
                    ],
                    max_length=20
                )),
                ('difficulty', models.CharField(
                    choices=[
                        ('easy', 'Easy'),
                        ('medium', 'Medium'),
                        ('hard', 'Hard')
                    ],
                    default='medium',
                    max_length=20
                )),
                ('target_grade', models.IntegerField(help_text='Target grade level (1-12)')),
                ('due_date', models.DateTimeField(blank=True, null=True)),
                ('is_published', models.BooleanField(default=False, help_text='Visible to students')),
                ('max_points', models.IntegerField(default=100)),
                ('instructions', models.TextField(blank=True)),
                ('time_limit_minutes', models.IntegerField(blank=True, help_text='Time limit in minutes', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('classroom', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='app.classroomgroup')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_assignments', to=settings.AUTH_USER_MODEL)),
                ('curriculum_standards', models.ManyToManyField(blank=True, help_text='Related curriculum standards', related_name='assignments', to='app.curriculumstandard')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),

        # Create AssignmentQuestion
        migrations.CreateModel(
            name='AssignmentQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question_order', models.IntegerField(default=0, help_text='Display order')),
                ('question_type', models.CharField(
                    choices=[
                        ('multiple_choice', 'Multiple Choice'),
                        ('calculation', 'Calculation'),
                        ('conversion', 'Currency Conversion'),
                        ('explanation', 'Written Explanation'),
                        ('true_false', 'True/False')
                    ],
                    max_length=30
                )),
                ('question_text', models.TextField()),
                ('correct_answer', models.TextField()),
                ('answer_options', models.JSONField(blank=True, default=list, help_text='For multiple choice questions')),
                ('points', models.IntegerField(default=10)),
                ('hints', models.JSONField(blank=True, default=list, help_text='List of hints')),
                ('explanation', models.TextField(blank=True, help_text='Explanation of correct answer')),
                ('currencies_involved', models.JSONField(blank=True, default=list, help_text="e.g., ['JPY', 'USD']")),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='app.assignment')),
            ],
            options={
                'ordering': ['assignment', 'question_order'],
            },
        ),

        # Create StudentSubmission
        migrations.CreateModel(
            name='StudentSubmission',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(
                    choices=[
                        ('not_started', 'Not Started'),
                        ('in_progress', 'In Progress'),
                        ('submitted', 'Submitted'),
                        ('graded', 'Graded')
                    ],
                    default='not_started',
                    max_length=20
                )),
                ('submitted_at', models.DateTimeField(blank=True, null=True)),
                ('total_score', models.IntegerField(blank=True, null=True)),
                ('feedback', models.TextField(blank=True, help_text="Teacher's overall feedback")),
                ('graded_at', models.DateTimeField(blank=True, null=True)),
                ('time_spent_seconds', models.IntegerField(default=0, help_text='Total time spent in seconds')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='app.assignment')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to=settings.AUTH_USER_MODEL)),
                ('graded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='graded_submissions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-submitted_at'],
            },
        ),

        # Create StudentAnswer
        migrations.CreateModel(
            name='StudentAnswer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer_text', models.TextField()),
                ('is_correct', models.BooleanField(blank=True, help_text='Set when graded', null=True)),
                ('points_earned', models.IntegerField(default=0)),
                ('teacher_comment', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('submission', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', to='app.studentsubmission')),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_answers', to='app.assignmentquestion')),
            ],
        ),

        # Create LessonPlan
        migrations.CreateModel(
            name='LessonPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('grade_level', models.IntegerField(help_text='Target grade level (1-12)')),
                ('duration_minutes', models.IntegerField(help_text='Expected lesson duration')),
                ('learning_objectives', models.JSONField(default=list, help_text='List of learning objectives')),
                ('materials_needed', models.JSONField(default=list, help_text='Required materials')),
                ('activity_sequence', models.JSONField(default=list, help_text='Step-by-step activities')),
                ('assessment_methods', models.JSONField(default=list, help_text='How to assess learning')),
                ('currencies_covered', models.JSONField(default=list, help_text='Currency codes covered in lesson')),
                ('ai_generated', models.BooleanField(default=False, help_text='Was this generated by AI')),
                ('template_used', models.CharField(blank=True, max_length=100, null=True)),
                ('is_public', models.BooleanField(default=False, help_text='Share with other teachers')),
                ('downloads_count', models.IntegerField(default=0)),
                ('rating_average', models.FloatField(default=0.0)),
                ('rating_count', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lesson_plans', to=settings.AUTH_USER_MODEL)),
                ('curriculum_standards', models.ManyToManyField(blank=True, related_name='lesson_plans', to='app.curriculumstandard')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),

        # Create Worksheet
        migrations.CreateModel(
            name='Worksheet',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('worksheet_type', models.CharField(
                    choices=[
                        ('practice', 'Practice'),
                        ('assessment', 'Assessment'),
                        ('homework', 'Homework'),
                        ('activity', 'Activity')
                    ],
                    max_length=20
                )),
                ('grade_level', models.IntegerField(help_text='Target grade level (1-12)')),
                ('content', models.TextField(help_text='Worksheet content (markdown or HTML)')),
                ('answer_key', models.TextField(blank=True)),
                ('pdf_file', models.FileField(blank=True, null=True, upload_to='worksheets/')),
                ('download_count', models.IntegerField(default=0)),
                ('is_public', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='worksheets', to=settings.AUTH_USER_MODEL)),
                ('lesson_plan', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='worksheets', to='app.lessonplan')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),

        # Create TeacherResource
        migrations.CreateModel(
            name='TeacherResource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('resource_type', models.CharField(
                    choices=[
                        ('lesson_plan', 'Lesson Plan'),
                        ('worksheet', 'Worksheet'),
                        ('activity', 'Activity'),
                        ('video', 'Video'),
                        ('link', 'External Link'),
                        ('presentation', 'Presentation')
                    ],
                    max_length=20
                )),
                ('file', models.FileField(blank=True, null=True, upload_to='teacher_resources/')),
                ('external_url', models.URLField(blank=True, null=True)),
                ('grade_levels', models.JSONField(default=list, help_text='Applicable grade levels')),
                ('subjects', models.JSONField(default=list, help_text='Applicable subjects')),
                ('is_free', models.BooleanField(default=True)),
                ('price', models.DecimalField(decimal_places=2, default=0, help_text='Price in USD', max_digits=6)),
                ('downloads', models.IntegerField(default=0)),
                ('rating', models.FloatField(default=0.0)),
                ('rating_count', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_resources', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),

        # Add indexes
        migrations.AddIndex(
            model_name='classroomgroup',
            index=models.Index(fields=['teacher', 'is_active'], name='app_classro_teacher_idx'),
        ),
        migrations.AddIndex(
            model_name='classroomgroup',
            index=models.Index(fields=['school_year', 'grade_level'], name='app_classro_school_idx'),
        ),
        migrations.AddIndex(
            model_name='curriculumstandard',
            index=models.Index(fields=['country', 'grade_level', 'subject'], name='app_curricu_country_idx'),
        ),
        migrations.AddIndex(
            model_name='curriculumstandard',
            index=models.Index(fields=['standard_code'], name='app_curricu_standar_idx'),
        ),
        migrations.AddIndex(
            model_name='assignment',
            index=models.Index(fields=['classroom', 'is_published'], name='app_assignm_classro_idx'),
        ),
        migrations.AddIndex(
            model_name='assignment',
            index=models.Index(fields=['teacher', 'created_at'], name='app_assignm_teacher_idx'),
        ),
        migrations.AddIndex(
            model_name='assignment',
            index=models.Index(fields=['due_date'], name='app_assignm_due_dat_idx'),
        ),
        migrations.AddIndex(
            model_name='assignmentquestion',
            index=models.Index(fields=['assignment', 'question_order'], name='app_assignm_assignm_idx'),
        ),
        migrations.AddIndex(
            model_name='studentsubmission',
            index=models.Index(fields=['assignment', 'status'], name='app_student_assignm_idx'),
        ),
        migrations.AddIndex(
            model_name='studentsubmission',
            index=models.Index(fields=['student', 'submitted_at'], name='app_student_student_idx'),
        ),
        migrations.AddIndex(
            model_name='studentanswer',
            index=models.Index(fields=['submission', 'question'], name='app_student_submiss_idx'),
        ),
        migrations.AddIndex(
            model_name='lessonplan',
            index=models.Index(fields=['teacher', 'created_at'], name='app_lessonp_teacher_idx'),
        ),
        migrations.AddIndex(
            model_name='lessonplan',
            index=models.Index(fields=['grade_level', 'is_public'], name='app_lessonp_grade_l_idx'),
        ),
        migrations.AddIndex(
            model_name='lessonplan',
            index=models.Index(fields=['-rating_average', '-downloads_count'], name='app_lessonp_rating__idx'),
        ),
        migrations.AddIndex(
            model_name='worksheet',
            index=models.Index(fields=['teacher', 'created_at'], name='app_workshe_teacher_idx'),
        ),
        migrations.AddIndex(
            model_name='worksheet',
            index=models.Index(fields=['grade_level', 'worksheet_type'], name='app_workshe_grade_l_idx'),
        ),
        migrations.AddIndex(
            model_name='teacherresource',
            index=models.Index(fields=['resource_type', '-downloads'], name='app_teacher_resourc_idx'),
        ),
        migrations.AddIndex(
            model_name='teacherresource',
            index=models.Index(fields=['-rating', '-downloads'], name='app_teacher_rating__idx'),
        ),

        # Add unique constraints
        migrations.AlterUniqueTogether(
            name='curriculumstandard',
            unique_together={('country', 'framework', 'standard_code')},
        ),
        migrations.AlterUniqueTogether(
            name='studentsubmission',
            unique_together={('assignment', 'student')},
        ),
        migrations.AlterUniqueTogether(
            name='studentanswer',
            unique_together={('submission', 'question')},
        ),
    ]
