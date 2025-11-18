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
        """Create subscription plans for all three phases"""
        plans = [
            # ==================================================================
            # Original Plans (General Use)
            # ==================================================================
            {
                'name': 'Free Plan',
                'plan_type': 'free',
                'price': 0.00,
                'billing_period': 'monthly',
                'ai_chat_limit': 5,
                'image_recognition_limit': 10,
                'max_students': 1,
                'max_assignments': 0,
                'ai_lesson_plans_limit': 0,
                'worksheet_generation_limit': 0,
                'max_rate_alerts': 0,
                'comparison_history_days': 30,
                'max_virtual_portfolios': 0,
                'max_open_trades': 0,
                'historical_data_days': 30,
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
                'billing_period': 'monthly',
                'ai_chat_limit': -1,  # Unlimited
                'image_recognition_limit': -1,  # Unlimited
                'max_students': 1,
                'max_assignments': 0,
                'ai_lesson_plans_limit': 0,
                'worksheet_generation_limit': 0,
                'max_rate_alerts': 0,
                'comparison_history_days': 30,
                'max_virtual_portfolios': 0,
                'max_open_trades': 0,
                'historical_data_days': 30,
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
                'billing_period': 'monthly',
                'ai_chat_limit': -1,
                'image_recognition_limit': -1,
                'max_students': 30,
                'max_assignments': 10,
                'ai_lesson_plans_limit': 5,
                'worksheet_generation_limit': 10,
                'max_rate_alerts': 0,
                'comparison_history_days': 30,
                'max_virtual_portfolios': 0,
                'max_open_trades': 0,
                'historical_data_days': 30,
                'features': {
                    'teacher_dashboard': True,
                    'class_management': True,
                    'student_reports': True,
                    'assignments': True,
                    'no_ads': True,
                    'priority_support': True,
                }
            },
            {
                'name': 'School Plan',
                'plan_type': 'school',
                'price': 99.00,
                'billing_period': 'yearly',
                'ai_chat_limit': -1,
                'image_recognition_limit': -1,
                'max_students': -1,
                'max_assignments': -1,
                'ai_lesson_plans_limit': -1,
                'worksheet_generation_limit': -1,
                'max_rate_alerts': 0,
                'comparison_history_days': 30,
                'max_virtual_portfolios': 0,
                'max_open_trades': 0,
                'historical_data_days': 30,
                'features': {
                    'unlimited_teachers': True,
                    'unlimited_students': True,
                    'shared_resources': True,
                    'admin_dashboard': True,
                    'custom_branding': True,
                    'no_ads': True,
                    'priority_support': True,
                }
            },

            # ==================================================================
            # Phase 1: Teacher-Focused Plans
            # ==================================================================
            {
                'name': 'Teacher Free',
                'plan_type': 'teacher_free',
                'price': 0.00,
                'billing_period': 'monthly',
                'ai_chat_limit': 10,
                'image_recognition_limit': 20,
                'max_students': 30,
                'max_assignments': 10,
                'ai_lesson_plans_limit': 3,  # per month
                'worksheet_generation_limit': 5,  # per month
                'max_rate_alerts': 0,
                'comparison_history_days': 30,
                'max_virtual_portfolios': 0,
                'max_open_trades': 0,
                'historical_data_days': 30,
                'features': {
                    'assignment_creation': True,
                    'basic_grading': True,
                    'student_progress': True,
                    'basic_analytics': True,
                    'curriculum_mapping': True,
                    'ai_lesson_plans_basic': True,
                    'worksheet_generation_basic': True,
                }
            },
            {
                'name': 'Teacher Pro',
                'plan_type': 'teacher_pro',
                'price': 9.99,
                'billing_period': 'monthly',
                'ai_chat_limit': -1,
                'image_recognition_limit': -1,
                'max_students': 100,
                'max_assignments': -1,
                'ai_lesson_plans_limit': -1,
                'worksheet_generation_limit': -1,
                'max_rate_alerts': 0,
                'comparison_history_days': 30,
                'max_virtual_portfolios': 0,
                'max_open_trades': 0,
                'historical_data_days': 30,
                'features': {
                    'unlimited_assignments': True,
                    'auto_grading': True,
                    'advanced_analytics': True,
                    'parent_notifications': True,
                    'custom_curriculum': True,
                    'ai_lesson_plans_unlimited': True,
                    'worksheet_generation_unlimited': True,
                    'pdf_export': True,
                    'no_ads': True,
                    'priority_support': True,
                }
            },
            {
                'name': 'District Plan',
                'plan_type': 'district',
                'price': 999.00,
                'billing_period': 'yearly',
                'ai_chat_limit': -1,
                'image_recognition_limit': -1,
                'max_students': -1,
                'max_assignments': -1,
                'ai_lesson_plans_limit': -1,
                'worksheet_generation_limit': -1,
                'max_rate_alerts': 0,
                'comparison_history_days': 30,
                'max_virtual_portfolios': 0,
                'max_open_trades': 0,
                'historical_data_days': 30,
                'features': {
                    'unlimited_schools': True,
                    'district_analytics': True,
                    'api_access': True,
                    'dedicated_support': True,
                    'custom_integrations': True,
                    'sso_support': True,
                    'white_label': True,
                }
            },

            # ==================================================================
            # Phase 2: Remittance User Plans
            # ==================================================================
            {
                'name': 'Remittance Free',
                'plan_type': 'remittance_free',
                'price': 0.00,
                'billing_period': 'monthly',
                'ai_chat_limit': 3,
                'image_recognition_limit': 5,
                'max_students': 0,
                'max_assignments': 0,
                'ai_lesson_plans_limit': 0,
                'worksheet_generation_limit': 0,
                'max_rate_alerts': 1,
                'comparison_history_days': 30,
                'max_virtual_portfolios': 0,
                'max_open_trades': 0,
                'historical_data_days': 30,
                'features': {
                    'rate_comparison': True,
                    'basic_alerts': True,
                    'transfer_history_30days': True,
                    'provider_comparison': True,
                }
            },
            {
                'name': 'Remittance Pro',
                'plan_type': 'remittance_pro',
                'price': 4.99,
                'billing_period': 'monthly',
                'ai_chat_limit': -1,
                'image_recognition_limit': -1,
                'max_students': 0,
                'max_assignments': 0,
                'ai_lesson_plans_limit': 0,
                'worksheet_generation_limit': 0,
                'max_rate_alerts': -1,  # Unlimited
                'comparison_history_days': -1,  # Unlimited
                'max_virtual_portfolios': 0,
                'max_open_trades': 0,
                'historical_data_days': 30,
                'features': {
                    'unlimited_alerts': True,
                    'ai_predictions': True,
                    'sms_notifications': True,
                    'transfer_groups': True,
                    'best_time_prediction': True,
                    'affiliate_tracking': True,
                    'no_ads': True,
                    'priority_support': True,
                }
            },

            # ==================================================================
            # Phase 3: Trading Plans
            # ==================================================================
            {
                'name': 'Trader Free',
                'plan_type': 'trader_free',
                'price': 0.00,
                'billing_period': 'monthly',
                'ai_chat_limit': 5,
                'image_recognition_limit': 0,
                'max_students': 0,
                'max_assignments': 0,
                'ai_lesson_plans_limit': 0,
                'worksheet_generation_limit': 0,
                'max_rate_alerts': 0,
                'comparison_history_days': 30,
                'max_virtual_portfolios': 1,
                'max_open_trades': 5,
                'historical_data_days': 30,
                'features': {
                    'virtual_trading': True,
                    'basic_charts': True,
                    'basic_indicators': True,
                    'leaderboard': True,
                    'community_access': True,
                }
            },
            {
                'name': 'Trader Pro',
                'plan_type': 'trader_pro',
                'price': 29.00,
                'billing_period': 'monthly',
                'ai_chat_limit': -1,
                'image_recognition_limit': 0,
                'max_students': 0,
                'max_assignments': 0,
                'ai_lesson_plans_limit': 0,
                'worksheet_generation_limit': 0,
                'max_rate_alerts': 0,
                'comparison_history_days': 30,
                'max_virtual_portfolios': 5,
                'max_open_trades': 50,
                'historical_data_days': 365,
                'features': {
                    'advanced_charts': True,
                    'all_indicators': True,
                    'premium_signals': True,
                    'strategy_backtesting': True,
                    'real_time_data': True,
                    'trade_analytics': True,
                    'no_ads': True,
                }
            },
            {
                'name': 'Trader Premium',
                'plan_type': 'trader_premium',
                'price': 99.00,
                'billing_period': 'monthly',
                'ai_chat_limit': -1,
                'image_recognition_limit': 0,
                'max_students': 0,
                'max_assignments': 0,
                'ai_lesson_plans_limit': 0,
                'worksheet_generation_limit': 0,
                'max_rate_alerts': 0,
                'comparison_history_days': 30,
                'max_virtual_portfolios': -1,  # Unlimited
                'max_open_trades': -1,  # Unlimited
                'historical_data_days': -1,  # Unlimited
                'features': {
                    'all_pro_features': True,
                    'auto_trading_bot': True,
                    'dedicated_analyst': True,
                    'api_access': True,
                    'custom_indicators': True,
                    'signal_marketplace': True,
                    'white_label_portfolios': True,
                    'priority_support': True,
                }
            },
        ]

        for plan_data in plans:
            plan, created = SubscriptionPlan.objects.update_or_create(
                plan_type=plan_data['plan_type'],
                defaults=plan_data
            )

            if created:
                self.stdout.write(f'  ✓ Created plan: {plan.name}')
            else:
                self.stdout.write(f'  ↻ Updated plan: {plan.name}')

    def _create_achievements(self):
        """Create initial achievements for gamification"""
        achievements = [
            # General achievements
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
            # Teacher achievements
            {
                'name': 'First Assignment',
                'description': 'Create your first assignment',
                'icon': '📝',
                'points_required': 0,
                'activity_count_required': 1,
                'activity_type': 'assignment_created',
            },
            {
                'name': 'Dedicated Teacher',
                'description': 'Grade 50 student submissions',
                'icon': '👨‍🏫',
                'points_required': 0,
                'activity_count_required': 50,
                'activity_type': 'submission_graded',
            },
            {
                'name': 'Lesson Planner',
                'description': 'Create 10 lesson plans',
                'icon': '📚',
                'points_required': 0,
                'activity_count_required': 10,
                'activity_type': 'lesson_plan_created',
            },
        ]

        for achievement_data in achievements:
            achievement, created = Achievement.objects.get_or_create(
                name=achievement_data['name'],
                defaults=achievement_data
            )

            if created:
                self.stdout.write(f'  ✓ Created achievement: {achievement.name}')
            else:
                self.stdout.write(f'  → Achievement already exists: {achievement.name}')
