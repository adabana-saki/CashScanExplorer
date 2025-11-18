"""
Authentication and user management views
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db import transaction
import logging

from .models import UserProfile, Subscription, SubscriptionPlan, UsageStatistics

logger = logging.getLogger(__name__)


def signup_view(request):
    """User registration view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        role = request.POST.get('role', 'student')
        age = request.POST.get('age')
        parent_email = request.POST.get('parent_email')

        # Validation
        if not all([username, email, password, password_confirm]):
            messages.error(request, 'All fields are required')
            return render(request, 'app/auth/signup.html')

        if password != password_confirm:
            messages.error(request, 'Passwords do not match')
            return render(request, 'app/auth/signup.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'app/auth/signup.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return render(request, 'app/auth/signup.html')

        try:
            with transaction.atomic():
                # Create user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )

                # Create user profile
                UserProfile.objects.create(
                    user=user,
                    role=role,
                    age=int(age) if age else None,
                    parent_email=parent_email if parent_email else None
                )

                # Assign free plan to new user
                free_plan = SubscriptionPlan.objects.get(plan_type='free')
                Subscription.objects.create(
                    user=user,
                    plan=free_plan,
                    status='active'
                )

                # Log the user in
                login(request, user)
                messages.success(request, 'Account created successfully!')
                return redirect('app:home')

        except SubscriptionPlan.DoesNotExist:
            messages.error(request, 'System error: Free plan not found. Please contact support.')
            return render(request, 'app/auth/signup.html')
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            messages.error(request, 'An error occurred during registration')
            return render(request, 'app/auth/signup.html')

    return render(request, 'app/auth/signup.html')


def login_view(request):
    """User login view"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, 'Username and password are required')
            return render(request, 'app/auth/login.html')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')

            # Redirect to next parameter or home
            next_url = request.GET.get('next', 'app:home')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password')
            return render(request, 'app/auth/login.html')

    return render(request, 'app/auth/login.html')


@login_required
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('app:home')


@login_required
def profile_view(request):
    """User profile and dashboard view"""
    # Optimize: Use select_related to fetch related objects in a single query
    user = User.objects.select_related('profile').prefetch_related(
        'learning_progress', 'achievements'
    ).get(pk=request.user.pk)

    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        # Create profile if it doesn't exist
        profile = UserProfile.objects.create(user=user)

    # Optimize: Use select_related for subscription and plan
    try:
        subscription = Subscription.objects.select_related('plan').get(user=user)
    except Subscription.DoesNotExist:
        # Assign free plan if no subscription exists
        free_plan = SubscriptionPlan.objects.get(plan_type='free')
        subscription = Subscription.objects.create(
            user=user,
            plan=free_plan,
            status='active'
        )

    # Get usage statistics for today
    usage_stats = {
        'ai_chat': UsageStatistics.get_today_usage(user, 'ai_chat'),
        'image_recognition': UsageStatistics.get_today_usage(user, 'image_recognition'),
    }

    # Calculate limits
    plan = subscription.plan
    limits = {
        'ai_chat': plan.ai_chat_limit,
        'image_recognition': plan.image_recognition_limit,
    }

    # Get learning progress (already prefetched)
    learning_progress_list = list(user.learning_progress.all()[:10])

    # Get achievements (already prefetched)
    achievements = user.achievements.all()[:10]

    # Optimize: Calculate total points from the prefetched learning_progress
    # Use aggregate to calculate sum efficiently
    from django.db.models import Sum
    total_points = user.learning_progress.aggregate(
        total=Sum('points_earned')
    )['total'] or 0

    context = {
        'profile': profile,
        'subscription': subscription,
        'usage_stats': usage_stats,
        'limits': limits,
        'learning_progress': learning_progress_list,
        'achievements': achievements,
        'total_points': total_points,
    }

    return render(request, 'app/auth/profile.html', context)


@login_required
@require_http_methods(["POST"])
def update_profile(request):
    """Update user profile information"""
    try:
        profile = request.user.profile

        # Update fields
        if 'age' in request.POST:
            age = request.POST.get('age')
            profile.age = int(age) if age else None

        if 'parent_email' in request.POST:
            profile.parent_email = request.POST.get('parent_email')

        if 'organization' in request.POST:
            profile.organization = request.POST.get('organization')

        profile.save()

        return JsonResponse({
            'success': True,
            'message': 'Profile updated successfully'
        })

    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
def usage_stats_api(request):
    """API endpoint to get current usage statistics"""
    user = request.user

    try:
        subscription = user.subscription
        plan = subscription.plan

        ai_chat_usage = UsageStatistics.get_today_usage(user, 'ai_chat')
        image_recognition_usage = UsageStatistics.get_today_usage(user, 'image_recognition')

        return JsonResponse({
            'success': True,
            'usage': {
                'ai_chat': {
                    'used': ai_chat_usage,
                    'limit': plan.ai_chat_limit,
                    'remaining': plan.ai_chat_limit - ai_chat_usage if plan.ai_chat_limit > 0 else -1
                },
                'image_recognition': {
                    'used': image_recognition_usage,
                    'limit': plan.image_recognition_limit,
                    'remaining': plan.image_recognition_limit - image_recognition_usage if plan.image_recognition_limit > 0 else -1
                }
            },
            'plan': {
                'name': plan.name,
                'type': plan.plan_type
            }
        })

    except Subscription.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'No subscription found'
        }, status=404)
