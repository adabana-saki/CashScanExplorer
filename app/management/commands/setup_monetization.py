"""
Management command to set up initial subscription plans and sample achievements
"""
from django.core.management.base import BaseCommand
from django.db import transaction
from app.models import SubscriptionPlan, Achievement


class Command(BaseCommand):
    help = 'Set up initial subscription plans and achievements for monetization'

    def handle(self, *args, **options):
        self.stdout.write('Setting up monetization system...')

        try:
            with transaction.atomic():
                # Create subscription plans
                self._create_subscription_plans()

                # Create initial achievements
                self._create_achievements()

            self.stdout.write(self.style.SUCCESS('Successfully set up monetization system!'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error setting up monetization: {e}'))

    def _create_subscription_plans(self):
        """Create subscription plans"""
        plans = [
            {
                'name': 'Free Plan',
                'plan_type': 'free',
                'price': 0.00,
                'ai_chat_limit': 5,
                'image_recognition_limit': 10,
                'max_students': 1,
                'features': {
                    'exchange_rate': True,
                    'currency_converter': True,
                    'basic_chat': True,
                    'basic_image_recognition': True,
                    'ads': True,
                }
            },
            {
                'name': 'Premium Plan',
                'plan_type': 'premium',
                'price': 2.99,
                'ai_chat_limit': -1,  # Unlimited
                'image_recognition_limit': -1,  # Unlimited
                'max_students': 1,
                'features': {
                    'exchange_rate': True,
                    'currency_converter': True,
                    'unlimited_chat': True,
                    'unlimited_image_recognition': True,
                    'learning_progress': True,
                    'achievements': True,
                    'parent_reports': True,
                    'no_ads': True,
                }
            },
            {
                'name': 'Classroom Plan',
                'plan_type': 'classroom',
                'price': 19.99,
                'ai_chat_limit': -1,  # Unlimited
                'image_recognition_limit': -1,  # Unlimited
                'max_students': 30,
                'features': {
                    'exchange_rate': True,
                    'currency_converter': True,
                    'unlimited_chat': True,
                    'unlimited_image_recognition': True,
                    'learning_progress': True,
                    'achievements': True,
                    'teacher_dashboard': True,
                    'class_management': True,
                    'student_reports': True,
                    'no_ads': True,
                    'priority_support': True,
                }
            },
            {
                'name': 'School Plan',
                'plan_type': 'school',
                'price': 49.99,
                'ai_chat_limit': -1,  # Unlimited
                'image_recognition_limit': -1,  # Unlimited
                'max_students': 100,
                'features': {
                    'exchange_rate': True,
                    'currency_converter': True,
                    'unlimited_chat': True,
                    'unlimited_image_recognition': True,
                    'learning_progress': True,
                    'achievements': True,
                    'teacher_dashboard': True,
                    'class_management': True,
                    'detailed_analytics': True,
                    'student_reports': True,
                    'custom_content': True,
                    'no_ads': True,
                    'priority_support': True,
                    'api_access': True,
                }
            }
        ]

        for plan_data in plans:
            plan, created = SubscriptionPlan.objects.update_or_create(
                plan_type=plan_data['plan_type'],
                defaults=plan_data
            )

            if created:
                self.stdout.write(f'  Created plan: {plan.name}')
            else:
                self.stdout.write(f'  Updated plan: {plan.name}')

    def _create_achievements(self):
        """Create initial achievements for gamification"""
        achievements = [
            {
                'name': 'First Steps',
                'description': 'Complete your first AI chat conversation',
                'icon': '🎯',
                'points_required': 0,
                'activity_count_required': 1,
                'activity_type': 'ai_chat_completed',
            },
            {
                'name': 'Currency Explorer',
                'description': 'Recognize your first currency with image recognition',
                'icon': '🔍',
                'points_required': 0,
                'activity_count_required': 1,
                'activity_type': 'image_recognized',
            },
            {
                'name': 'Exchange Master',
                'description': 'Check exchange rates 10 times',
                'icon': '💱',
                'points_required': 0,
                'activity_count_required': 10,
                'activity_type': 'exchange_rate_checked',
            },
            {
                'name': 'Chat Expert',
                'description': 'Complete 25 AI chat conversations',
                'icon': '💬',
                'points_required': 0,
                'activity_count_required': 25,
                'activity_type': 'ai_chat_completed',
            },
            {
                'name': 'Money Detective',
                'description': 'Use image recognition 50 times',
                'icon': '🕵️',
                'points_required': 0,
                'activity_count_required': 50,
                'activity_type': 'image_recognized',
            },
            {
                'name': 'Financial Genius',
                'description': 'Earn 500 learning points',
                'icon': '🌟',
                'points_required': 500,
                'activity_count_required': 0,
                'activity_type': None,
            },
            {
                'name': 'Super Learner',
                'description': 'Earn 1000 learning points',
                'icon': '⭐',
                'points_required': 1000,
                'activity_count_required': 0,
                'activity_type': None,
            },
        ]

        for achievement_data in achievements:
            achievement, created = Achievement.objects.get_or_create(
                name=achievement_data['name'],
                defaults=achievement_data
            )

            if created:
                self.stdout.write(f'  Created achievement: {achievement.name}')
            else:
                self.stdout.write(f'  Achievement already exists: {achievement.name}')
