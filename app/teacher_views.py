"""
Teacher-focused views for Phase 1
Handles classroom management, assignments, grading, and lesson planning
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Avg, Q, Sum
from django.utils import timezone
from django.contrib import messages
from datetime import datetime, timedelta
import random
import string
import logging

from .models import (
    ClassroomGroup, Assignment, AssignmentQuestion, StudentSubmission,
    StudentAnswer, LessonPlan, Worksheet, CurriculumStandard,
    TeacherResource, LearningProgress
)

logger = logging.getLogger(__name__)


def teacher_required(view_func):
    """Decorator to ensure user is a teacher"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to access this page.')
            return redirect('app:login')

        try:
            if request.user.profile.role != 'teacher':
                messages.error(request, 'This page is only accessible to teachers.')
                return redirect('app:home')
        except:
            messages.error(request, 'Profile not found. Please contact support.')
            return redirect('app:home')

        return view_func(request, *args, **kwargs)
    return wrapper


# ============================================================================
# Teacher Dashboard
# ============================================================================

@login_required
@teacher_required
def teacher_dashboard(request):
    """
    Main dashboard for teachers
    Shows overview of classrooms, assignments, and student progress
    """
    teacher = request.user

    # Get teacher's classrooms with student count
    classrooms = ClassroomGroup.objects.filter(
        teacher=teacher,
        is_active=True
    ).prefetch_related('students').annotate(
        student_count=Count('students')
    ).order_by('-created_at')

    # Get recent assignments
    recent_assignments = Assignment.objects.filter(
        teacher=teacher
    ).select_related('classroom').order_by('-created_at')[:5]

    # Get assignments needing grading
    pending_grading = StudentSubmission.objects.filter(
        assignment__teacher=teacher,
        status='submitted'
    ).select_related('assignment', 'student').order_by('submitted_at')[:10]

    # Calculate statistics
    total_students = sum(c.student_count for c in classrooms)
    total_assignments = Assignment.objects.filter(teacher=teacher).count()
    total_submissions = StudentSubmission.objects.filter(
        assignment__teacher=teacher
    ).count()
    pending_count = pending_grading.count()

    # Get recent activity
    recent_activity = LearningProgress.objects.filter(
        user__teaching_groups__teacher=teacher
    ).select_related('user').order_by('-timestamp')[:10]

    context = {
        'classrooms': classrooms,
        'recent_assignments': recent_assignments,
        'pending_grading': pending_grading,
        'stats': {
            'total_students': total_students,
            'total_assignments': total_assignments,
            'total_submissions': total_submissions,
            'pending_grading': pending_count,
        },
        'recent_activity': recent_activity,
    }

    return render(request, 'app/teacher/dashboard.html', context)


# ============================================================================
# Classroom Management
# ============================================================================

@login_required
@teacher_required
def classroom_list(request):
    """List all classrooms for the teacher"""
    classrooms = ClassroomGroup.objects.filter(
        teacher=request.user
    ).prefetch_related('students').annotate(
        student_count=Count('students'),
        assignment_count=Count('assignments')
    ).order_by('-created_at')

    context = {'classrooms': classrooms}
    return render(request, 'app/teacher/classroom_list.html', context)


@login_required
@teacher_required
def classroom_create(request):
    """Create a new classroom"""
    if request.method == 'POST':
        try:
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            grade_level = request.POST.get('grade_level')
            subject = request.POST.get('subject')
            school_year = request.POST.get('school_year')

            # Generate unique access code
            access_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            while ClassroomGroup.objects.filter(access_code=access_code).exists():
                access_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

            classroom = ClassroomGroup.objects.create(
                name=name,
                teacher=request.user,
                description=description,
                grade_level=int(grade_level) if grade_level else None,
                subject=subject,
                school_year=school_year,
                access_code=access_code
            )

            messages.success(request, f'Classroom "{name}" created successfully! Access code: {access_code}')
            return redirect('app:teacher_classroom_detail', classroom_id=classroom.id)

        except Exception as e:
            logger.error(f"Error creating classroom: {e}")
            messages.error(request, 'Failed to create classroom. Please try again.')

    # Get current school year
    now = datetime.now()
    current_year = now.year
    next_year = current_year + 1
    default_school_year = f"{current_year}-{next_year}"

    context = {
        'default_school_year': default_school_year,
        'grade_levels': range(1, 13),
    }
    return render(request, 'app/teacher/classroom_create.html', context)


@login_required
@teacher_required
def classroom_detail(request, classroom_id):
    """View detailed information about a classroom"""
    classroom = get_object_or_404(
        ClassroomGroup,
        id=classroom_id,
        teacher=request.user
    )

    # Get students with their progress
    students = classroom.students.all().prefetch_related(
        'submissions', 'learning_progress'
    )

    # Get assignments for this classroom
    assignments = Assignment.objects.filter(
        classroom=classroom
    ).annotate(
        submission_count=Count('submissions'),
        avg_score=Avg('submissions__total_score')
    ).order_by('-created_at')

    # Calculate classroom statistics
    total_students = students.count()
    total_assignments = assignments.count()

    context = {
        'classroom': classroom,
        'students': students,
        'assignments': assignments,
        'total_students': total_students,
        'total_assignments': total_assignments,
    }

    return render(request, 'app/teacher/classroom_detail.html', context)


# ============================================================================
# Assignment Management
# ============================================================================

@login_required
@teacher_required
def assignment_list(request):
    """List all assignments created by the teacher"""
    assignments = Assignment.objects.filter(
        teacher=request.user
    ).select_related('classroom').annotate(
        submission_count=Count('submissions'),
        graded_count=Count('submissions', filter=Q(submissions__status='graded'))
    ).order_by('-created_at')

    context = {'assignments': assignments}
    return render(request, 'app/teacher/assignment_list.html', context)


@login_required
@teacher_required
def assignment_create(request):
    """Create a new assignment"""
    if request.method == 'POST':
        try:
            classroom_id = request.POST.get('classroom')
            title = request.POST.get('title')
            description = request.POST.get('description')
            assignment_type = request.POST.get('assignment_type')
            difficulty = request.POST.get('difficulty', 'medium')
            target_grade = request.POST.get('target_grade')
            max_points = request.POST.get('max_points', 100)
            due_date = request.POST.get('due_date')
            instructions = request.POST.get('instructions', '')

            classroom = get_object_or_404(
                ClassroomGroup,
                id=classroom_id,
                teacher=request.user
            )

            assignment = Assignment.objects.create(
                classroom=classroom,
                teacher=request.user,
                title=title,
                description=description,
                assignment_type=assignment_type,
                difficulty=difficulty,
                target_grade=int(target_grade) if target_grade else classroom.grade_level or 1,
                max_points=int(max_points),
                due_date=due_date if due_date else None,
                instructions=instructions
            )

            messages.success(request, f'Assignment "{title}" created successfully!')
            return redirect('app:teacher_assignment_edit', assignment_id=assignment.id)

        except Exception as e:
            logger.error(f"Error creating assignment: {e}")
            messages.error(request, 'Failed to create assignment. Please try again.')

    # Get teacher's classrooms
    classrooms = ClassroomGroup.objects.filter(
        teacher=request.user,
        is_active=True
    ).order_by('-created_at')

    context = {
        'classrooms': classrooms,
        'assignment_types': Assignment.ASSIGNMENT_TYPE_CHOICES,
        'difficulties': Assignment.DIFFICULTY_CHOICES,
    }
    return render(request, 'app/teacher/assignment_create.html', context)


@login_required
@teacher_required
def assignment_edit(request, assignment_id):
    """Edit assignment and manage questions"""
    assignment = get_object_or_404(
        Assignment,
        id=assignment_id,
        teacher=request.user
    )

    if request.method == 'POST':
        try:
            # Update assignment fields
            assignment.title = request.POST.get('title', assignment.title)
            assignment.description = request.POST.get('description', assignment.description)
            assignment.difficulty = request.POST.get('difficulty', assignment.difficulty)
            assignment.max_points = int(request.POST.get('max_points', assignment.max_points))
            assignment.instructions = request.POST.get('instructions', assignment.instructions)

            due_date = request.POST.get('due_date')
            if due_date:
                assignment.due_date = due_date

            is_published = request.POST.get('is_published') == 'on'
            assignment.is_published = is_published

            assignment.save()

            messages.success(request, 'Assignment updated successfully!')
            return redirect('app:teacher_assignment_edit', assignment_id=assignment.id)

        except Exception as e:
            logger.error(f"Error updating assignment: {e}")
            messages.error(request, 'Failed to update assignment.')

    # Get questions for this assignment
    questions = AssignmentQuestion.objects.filter(
        assignment=assignment
    ).order_by('question_order')

    context = {
        'assignment': assignment,
        'questions': questions,
        'question_types': AssignmentQuestion.QUESTION_TYPE_CHOICES,
    }
    return render(request, 'app/teacher/assignment_edit.html', context)


@login_required
@teacher_required
@require_http_methods(["POST"])
def assignment_add_question(request, assignment_id):
    """Add a question to an assignment"""
    assignment = get_object_or_404(
        Assignment,
        id=assignment_id,
        teacher=request.user
    )

    try:
        question_text = request.POST.get('question_text')
        question_type = request.POST.get('question_type')
        correct_answer = request.POST.get('correct_answer')
        points = int(request.POST.get('points', 10))

        # Get the next question order
        last_question = AssignmentQuestion.objects.filter(
            assignment=assignment
        ).order_by('-question_order').first()

        next_order = (last_question.question_order + 1) if last_question else 1

        # Handle answer options for multiple choice
        answer_options = []
        if question_type == 'multiple_choice':
            for i in range(1, 5):
                option = request.POST.get(f'option_{i}')
                if option:
                    answer_options.append(option)

        question = AssignmentQuestion.objects.create(
            assignment=assignment,
            question_order=next_order,
            question_type=question_type,
            question_text=question_text,
            correct_answer=correct_answer,
            answer_options=answer_options,
            points=points
        )

        messages.success(request, 'Question added successfully!')

    except Exception as e:
        logger.error(f"Error adding question: {e}")
        messages.error(request, 'Failed to add question.')

    return redirect('app:teacher_assignment_edit', assignment_id=assignment.id)


# ============================================================================
# Grading
# ============================================================================

@login_required
@teacher_required
def grading_queue(request):
    """Show all submissions that need grading"""
    pending_submissions = StudentSubmission.objects.filter(
        assignment__teacher=request.user,
        status='submitted'
    ).select_related(
        'assignment', 'student', 'assignment__classroom'
    ).order_by('submitted_at')

    context = {'submissions': pending_submissions}
    return render(request, 'app/teacher/grading_queue.html', context)


@login_required
@teacher_required
def grade_submission(request, submission_id):
    """Grade a student's submission"""
    submission = get_object_or_404(
        StudentSubmission,
        id=submission_id,
        assignment__teacher=request.user
    )

    if request.method == 'POST':
        try:
            # Update each answer
            total_score = 0
            answers = StudentAnswer.objects.filter(submission=submission)

            for answer in answers:
                is_correct = request.POST.get(f'correct_{answer.id}') == 'on'
                points_earned = int(request.POST.get(f'points_{answer.id}', 0))
                teacher_comment = request.POST.get(f'comment_{answer.id}', '')

                answer.is_correct = is_correct
                answer.points_earned = points_earned
                answer.teacher_comment = teacher_comment
                answer.save()

                total_score += points_earned

            # Update submission
            submission.total_score = total_score
            submission.status = 'graded'
            submission.graded_at = timezone.now()
            submission.graded_by = request.user
            submission.feedback = request.POST.get('overall_feedback', '')
            submission.save()

            # Award learning progress points
            LearningProgress.objects.create(
                user=submission.student,
                activity_type='quiz_completed',
                details={
                    'assignment': submission.assignment.title,
                    'score': total_score,
                    'max_score': submission.assignment.max_points
                },
                points_earned=max(1, int(total_score / 10))  # 1 point per 10 score points
            )

            messages.success(request, f'Submission graded successfully! Score: {total_score}/{submission.assignment.max_points}')
            return redirect('app:teacher_grading_queue')

        except Exception as e:
            logger.error(f"Error grading submission: {e}")
            messages.error(request, 'Failed to grade submission.')

    # Get submission with answers and questions
    answers = StudentAnswer.objects.filter(
        submission=submission
    ).select_related('question').order_by('question__question_order')

    context = {
        'submission': submission,
        'answers': answers,
    }
    return render(request, 'app/teacher/grade_submission.html', context)


# ============================================================================
# Student Progress
# ============================================================================

@login_required
@teacher_required
def student_progress(request, classroom_id, student_id):
    """View detailed progress for a specific student"""
    classroom = get_object_or_404(
        ClassroomGroup,
        id=classroom_id,
        teacher=request.user
    )

    student = get_object_or_404(classroom.students, id=student_id)

    # Get student's submissions in this classroom
    submissions = StudentSubmission.objects.filter(
        student=student,
        assignment__classroom=classroom
    ).select_related('assignment').order_by('-submitted_at')

    # Calculate statistics
    total_submissions = submissions.count()
    graded_submissions = submissions.filter(status='graded')

    if graded_submissions.exists():
        avg_score = graded_submissions.aggregate(Avg('total_score'))['total_score__avg'] or 0
    else:
        avg_score = 0

    # Get learning progress
    learning_progress = LearningProgress.objects.filter(
        user=student
    ).order_by('-timestamp')[:20]

    context = {
        'classroom': classroom,
        'student': student,
        'submissions': submissions,
        'stats': {
            'total_submissions': total_submissions,
            'graded_count': graded_submissions.count(),
            'avg_score': round(avg_score, 1),
        },
        'learning_progress': learning_progress,
    }

    return render(request, 'app/teacher/student_progress.html', context)
