"""
Middleware for managing subscription-based access control and usage limits
"""
from django.http import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from .models import Subscription, UsageStatistics, SubscriptionPlan


class SubscriptionMiddleware:
    """
    Middleware to check user subscription status and enforce usage limits
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Define which URLs require subscription checks
        self.protected_paths = {
            '/app/ask/': 'ai_chat',
            '/app/video-feed/': 'image_recognition',
        }

    def __call__(self, request):
        # Check if the path requires subscription verification
        for path_prefix, feature in self.protected_paths.items():
            if request.path.startswith(path_prefix):
                if not request.user.is_authenticated:
                    # Anonymous users get free tier limits
                    return self._check_anonymous_limits(request, feature)
                else:
                    # Authenticated users - check their subscription
                    return self._check_subscription_limits(request, feature)

        response = self.get_response(request)
        return response

    def _check_anonymous_limits(self, request, feature):
        """
        Check limits for anonymous (non-logged-in) users
        Anonymous users are treated as free tier
        """
        # For anonymous users, we can use session or IP-based tracking
        # For now, we'll be lenient and let them proceed
        # In production, implement IP-based rate limiting here
        response = self.get_response(request)
        return response

    def _check_subscription_limits(self, request, feature):
        """
        Check subscription status and usage limits for authenticated users
        """
        user = request.user

        try:
            # Get user's subscription
            subscription = Subscription.objects.select_related('plan').get(user=user)

            # Check if subscription is valid
            if not subscription.is_valid():
                return JsonResponse({
                    'error': 'Your subscription has expired. Please renew to continue.',
                    'code': 'SUBSCRIPTION_EXPIRED',
                    'upgrade_url': reverse('app:pricing')
                }, status=403)

            # Get the plan limits
            plan = subscription.plan

            # Determine the limit for this feature
            if feature == 'ai_chat':
                limit = plan.ai_chat_limit
            elif feature == 'image_recognition':
                limit = plan.image_recognition_limit
            else:
                limit = -1  # Unlimited for other features

            # If unlimited (-1), allow access
            if limit == -1:
                response = self.get_response(request)
                return response

            # Check today's usage
            today_usage = UsageStatistics.get_today_usage(user, feature)

            if today_usage >= limit:
                return JsonResponse({
                    'error': f'Daily limit reached ({limit} per day). Upgrade to Premium for unlimited access.',
                    'code': 'LIMIT_REACHED',
                    'current_usage': today_usage,
                    'limit': limit,
                    'upgrade_url': reverse('app:pricing')
                }, status=429)

            # Proceed with the request
            response = self.get_response(request)
            return response

        except Subscription.DoesNotExist:
            # User doesn't have a subscription - assign them to free plan
            try:
                free_plan = SubscriptionPlan.objects.get(plan_type='free')
                Subscription.objects.create(
                    user=user,
                    plan=free_plan,
                    status='active'
                )
                # Recheck limits with new subscription
                return self._check_subscription_limits(request, feature)
            except SubscriptionPlan.DoesNotExist:
                return JsonResponse({
                    'error': 'Subscription system not configured. Please contact support.',
                    'code': 'SYSTEM_ERROR'
                }, status=500)


def check_feature_access(user, feature):
    """
    Helper function to check if a user has access to a feature
    Returns: (has_access: bool, remaining: int, limit: int, message: str)
    """
    if not user.is_authenticated:
        return False, 0, 0, "Please log in to use this feature"

    try:
        subscription = Subscription.objects.select_related('plan').get(user=user)

        if not subscription.is_valid():
            return False, 0, 0, "Your subscription has expired"

        plan = subscription.plan

        # Get the limit for this feature
        if feature == 'ai_chat':
            limit = plan.ai_chat_limit
        elif feature == 'image_recognition':
            limit = plan.image_recognition_limit
        else:
            return True, -1, -1, "Access granted"

        # Unlimited access
        if limit == -1:
            return True, -1, -1, "Unlimited access"

        # Check today's usage
        today_usage = UsageStatistics.get_today_usage(user, feature)
        remaining = max(0, limit - today_usage)

        if today_usage >= limit:
            return False, 0, limit, f"Daily limit of {limit} reached"

        return True, remaining, limit, "Access granted"

    except Subscription.DoesNotExist:
        return False, 0, 0, "No active subscription"


def increment_feature_usage(user, feature):
    """
    Helper function to increment usage count after successful use
    """
    if user.is_authenticated:
        UsageStatistics.increment_usage(user, feature)
