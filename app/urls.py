from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from . import auth_views
from . import subscription_views
from . import game_views

app_name = 'app'

# Main page URLs
urlpatterns = [
   path('', views.home, name='home'),
   path('get_updated_graph/', views.get_updated_graph, name='get_updated_graph'),
]

# Authentication URLs
urlpatterns += [
   path('signup/', auth_views.signup_view, name='signup'),
   path('login/', auth_views.login_view, name='login'),
   path('logout/', auth_views.logout_view, name='logout'),
   path('profile/', auth_views.profile_view, name='profile'),
   path('profile/update/', auth_views.update_profile, name='update_profile'),
   path('api/usage-stats/', auth_views.usage_stats_api, name='usage_stats_api'),
]

# Subscription and Payment URLs
urlpatterns += [
   path('pricing/', subscription_views.pricing_view, name='pricing'),
   path('create-checkout-session/', subscription_views.create_checkout_session, name='create_checkout_session'),
   path('payment/success/', subscription_views.payment_success, name='payment_success'),
   path('payment/cancel/', subscription_views.payment_cancel, name='payment_cancel'),
   path('cancel-subscription/', subscription_views.cancel_subscription, name='cancel_subscription'),
   path('webhook/stripe/', subscription_views.stripe_webhook, name='stripe_webhook'),
]

# Feature pages
urlpatterns += [
   path('exchange_rate/', views.exchange_rate, name='exchange_rate'),
   path('image_recognition/', views.image_recognition, name='image_recognition'),
   path('money/', views.money, name='money'),
   path('financing_ai_chat/', views.financing_ai_chat, name='financing_ai_chat'),
   path('reference/', views.reference, name='reference'),
]

# Learning Games URLs
urlpatterns += [
   path('games/quiz/', game_views.currency_quiz, name='currency_quiz'),
   path('games/quiz/generate/', game_views.generate_quiz_question, name='generate_quiz_question'),
   path('games/quiz/submit/', game_views.submit_quiz_answer, name='submit_quiz_answer'),
   path('games/comparison/', game_views.currency_comparison, name='currency_comparison'),
   path('games/travel-budget/', game_views.travel_budget_game, name='travel_budget_game'),
]

# API endpoints
urlpatterns += [
   path('convert/', views.convert_currency, name='convert_currency'),
   path('start_camera/', views.start_camera, name='start_camera'),
   path('video_feed/<str:stream_id>', views.video_feed, name='video_feed'),
   path('get_exchange_rates/', views.get_exchange_rates, name='get_exchange_rates'),
   path('ask/', views.ask, name='ask'),
]

# Static files
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)