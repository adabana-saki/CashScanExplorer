# CashScanExplorer - Complete Database Design
## 3-Phase Multi-Purpose Platform Architecture

Last Updated: 2025-11-18

---

## Overview

This database design supports three distinct user segments:
1. **Teachers & Students** - Educational platform for teaching currency/math
2. **Remittance Users** - Optimize international money transfers
3. **FX Traders** - Virtual trading and learning platform

---

## Core Models (Already Implemented)

### User Management
```
User (Django built-in)
├─ UserProfile
│  ├─ role: student, parent, teacher, admin, remittance_user, trader
│  ├─ age, parent_email, organization
│  └─ trader_experience_level (NEW)
│     └─ choices: beginner, intermediate, advanced, professional
│
├─ Subscription
│  ├─ plan: SubscriptionPlan (FK)
│  ├─ stripe_customer_id, stripe_subscription_id
│  └─ status: active, cancelled, expired, trial
│
└─ SubscriptionPlan
   ├─ plan_type: free, teacher_free, teacher_pro, school, district,
   │             remittance_free, remittance_pro, trader_free, trader_pro, trader_premium
   ├─ price (monthly in USD)
   ├─ ai_chat_limit, image_recognition_limit
   ├─ max_students, max_alerts, max_trades
   └─ features (JSONField)
```

### Currency Data
```
ExchangeRate
├─ date, rate, currency_pair
└─ Used by: conversion, charts, predictions, trading
```

### Activity Tracking
```
UsageStatistics
├─ user, feature, count, date
└─ Features: ai_chat, image_recognition, currency_conversion,
              rate_alert, trade_execution, signal_access

LearningProgress
├─ user, activity_type, details, points_earned, timestamp
└─ Activity types: currency_learned, quiz_completed, assignment_completed,
                   trade_executed, signal_followed, etc.
```

---

## Phase 1: Teacher-Focused Models

### Assignment System
```
Assignment
├─ id (PK)
├─ classroom: ClassroomGroup (FK)
├─ teacher: User (FK)
├─ title, description
├─ assignment_type: quiz, worksheet, project, custom
├─ difficulty: easy, medium, hard
├─ target_grade: 1-12
├─ curriculum_standards: [CurriculumStandard] (M2M)
├─ due_date, created_at, updated_at
├─ is_published: Boolean
├─ max_points: Integer
└─ instructions: TextField

AssignmentQuestion
├─ id (PK)
├─ assignment: Assignment (FK)
├─ question_order: Integer
├─ question_type: multiple_choice, calculation, conversion, explanation
├─ question_text: TextField
├─ correct_answer: TextField
├─ answer_options: JSONField (for multiple choice)
├─ points: Integer
├─ hints: JSONField
├─ explanation: TextField
└─ currencies_involved: JSONField (e.g., ["JPY", "USD"])

StudentSubmission
├─ id (PK)
├─ assignment: Assignment (FK)
├─ student: User (FK)
├─ submitted_at: DateTime
├─ status: not_started, in_progress, submitted, graded
├─ total_score: Integer
├─ feedback: TextField (teacher's comment)
├─ graded_at: DateTime
├─ graded_by: User (FK, nullable)
└─ time_spent: Integer (seconds)

StudentAnswer
├─ id (PK)
├─ submission: StudentSubmission (FK)
├─ question: AssignmentQuestion (FK)
├─ answer_text: TextField
├─ is_correct: Boolean (nullable, set when graded)
├─ points_earned: Integer
└─ teacher_comment: TextField (nullable)
```

### Lesson Planning
```
LessonPlan
├─ id (PK)
├─ teacher: User (FK)
├─ title, description
├─ grade_level: 1-12
├─ duration_minutes: Integer
├─ curriculum_standards: [CurriculumStandard] (M2M)
├─ learning_objectives: JSONField (list of objectives)
├─ materials_needed: JSONField
├─ activity_sequence: JSONField (step-by-step activities)
├─ assessment_methods: JSONField
├─ currencies_covered: JSONField
├─ ai_generated: Boolean
├─ template_used: CharField (nullable)
├─ is_public: Boolean (shareable with other teachers)
├─ downloads_count: Integer
├─ rating_average: Float
└─ created_at, updated_at

Worksheet
├─ id (PK)
├─ lesson_plan: LessonPlan (FK, nullable)
├─ teacher: User (FK)
├─ title, description
├─ worksheet_type: practice, assessment, homework, activity
├─ grade_level: 1-12
├─ content: TextField (rendered to PDF)
├─ answer_key: TextField
├─ pdf_file: FileField (generated PDF)
├─ download_count: Integer
├─ is_public: Boolean
└─ created_at

CurriculumStandard
├─ id (PK)
├─ country: US, UK, JP, AU, CA, etc.
├─ framework: Common Core, National Curriculum, etc.
├─ grade_level: 1-12
├─ subject: Math, Social Studies, Economics
├─ standard_code: CharField (e.g., "CCSS.MATH.4.MD.A.2")
├─ description: TextField
├─ related_currencies: JSONField
└─ parent_standard: Self (FK, nullable, for hierarchical standards)
```

### Teacher Dashboard Data
```
ClassroomGroup (EXTENDED)
├─ ... (existing fields)
├─ grade_level: 1-12
├─ school_year: CharField (e.g., "2024-2025")
├─ subject: Math, Economics, etc.
├─ meeting_schedule: JSONField (days/times)
└─ performance_metrics: JSONField (cached aggregated data)

TeacherResource
├─ id (PK)
├─ title, description
├─ resource_type: lesson_plan, worksheet, activity, video, link
├─ file: FileField (nullable)
├─ external_url: URLField (nullable)
├─ grade_levels: JSONField (list of applicable grades)
├─ subjects: JSONField
├─ created_by: User (FK)
├─ is_free: Boolean
├─ price: Decimal (for marketplace)
├─ downloads: Integer
├─ rating: Float
└─ created_at
```

---

## Phase 2: Remittance User Models

### Exchange Rate Alerts
```
ExchangeRateAlert
├─ id (PK)
├─ user: User (FK)
├─ from_currency: CharField (3 letters)
├─ to_currency: CharField (3 letters)
├─ target_rate: Decimal
├─ condition: above, below, equals
├─ is_active: Boolean
├─ notification_method: email, sms, push, all
├─ triggered_at: DateTime (nullable, when alert was triggered)
├─ triggered_rate: Decimal (nullable)
├─ frequency: once, daily, weekly (how often to check)
├─ expires_at: DateTime (nullable)
└─ created_at, updated_at

RateNotificationLog
├─ id (PK)
├─ alert: ExchangeRateAlert (FK)
├─ sent_at: DateTime
├─ notification_type: email, sms, push
├─ rate_at_notification: Decimal
└─ status: sent, failed, bounced
```

### Remittance Comparison
```
RemittanceProvider
├─ id (PK)
├─ name: Wise, Western Union, PayPal, MoneyGram, Remitly, etc.
├─ logo_url: URLField
├─ website_url: URLField
├─ supported_corridors: JSONField (list of from->to currency pairs)
├─ transfer_methods: JSONField (bank, card, cash pickup)
├─ typical_speed: CharField (instant, hours, 1-3 days)
├─ affiliate_url: URLField (nullable, for revenue)
├─ affiliate_commission: Decimal (nullable)
├─ api_available: Boolean
├─ is_active: Boolean
└─ last_updated: DateTime

RemittanceFee
├─ id (PK)
├─ provider: RemittanceProvider (FK)
├─ from_currency: CharField
├─ to_currency: CharField
├─ transfer_method: bank, card, cash
├─ fee_structure: flat, percentage, tiered
├─ base_fee: Decimal
├─ percentage_fee: Decimal
├─ minimum_fee: Decimal (nullable)
├─ maximum_fee: Decimal (nullable)
├─ exchange_rate_markup: Decimal (in percentage)
├─ min_amount: Decimal
├─ max_amount: Decimal
├─ effective_from: Date
├─ effective_to: Date (nullable)
└─ last_scraped: DateTime

RemittanceComparison
├─ id (PK)
├─ user: User (FK)
├─ from_currency: CharField
├─ to_currency: CharField
├─ send_amount: Decimal
├─ providers_compared: JSONField (list of provider IDs)
├─ best_provider: RemittanceProvider (FK, nullable)
├─ estimated_savings: Decimal
├─ comparison_data: JSONField (full comparison results)
├─ created_at: DateTime
└─ affiliate_click: Boolean (if user clicked affiliate link)
```

### Transfer History & Groups
```
RemittanceHistory
├─ id (PK)
├─ user: User (FK)
├─ from_currency: CharField
├─ to_currency: CharField
├─ send_amount: Decimal
├─ receive_amount: Decimal
├─ exchange_rate_used: Decimal
├─ provider: RemittanceProvider (FK, nullable)
├─ total_fees: Decimal
├─ transfer_date: Date
├─ recipient_name: CharField
├─ recipient_country: CharField
├─ notes: TextField (nullable)
├─ reference_number: CharField (nullable)
├─ status: pending, completed, cancelled
└─ created_at, updated_at

RemittanceGroup
├─ id (PK)
├─ name: CharField (e.g., "Family in Philippines")
├─ admin: User (FK, creator)
├─ members: [User] (M2M)
├─ default_from_currency: CharField
├─ default_to_currency: CharField
├─ total_sent: Decimal (lifetime)
├─ total_saved: Decimal (estimated via comparisons)
├─ recurring_schedule: JSONField (for scheduled reminders)
└─ created_at

RatePrediction
├─ id (PK)
├─ currency_pair: CharField
├─ prediction_date: Date
├─ predicted_rate: Decimal
├─ confidence_level: Float (0-1)
├─ prediction_model: CharField (ARIMA, LSTM, etc.)
├─ actual_rate: Decimal (nullable, filled after prediction_date)
├─ accuracy: Float (nullable, calculated after actual_rate is known)
├─ created_at: DateTime
└─ features_used: JSONField (technical indicators used)
```

---

## Phase 3: FX Trading Models

### Virtual Trading
```
VirtualPortfolio
├─ id (PK)
├─ user: User (FK)
├─ name: CharField (e.g., "Main Account", "Conservative Strategy")
├─ initial_balance: Decimal
├─ current_balance: Decimal
├─ currency: CharField (base currency, default USD)
├─ is_active: Boolean
├─ leverage: Integer (1x, 10x, 50x, etc.)
├─ risk_level: conservative, moderate, aggressive
├─ total_trades: Integer
├─ winning_trades: Integer
├─ losing_trades: Integer
├─ total_profit_loss: Decimal
├─ win_rate: Float (percentage)
├─ sharpe_ratio: Float (nullable)
├─ max_drawdown: Decimal
├─ created_at, updated_at
└─ reset_at: DateTime (nullable, if user resets portfolio)

Trade
├─ id (PK)
├─ portfolio: VirtualPortfolio (FK)
├─ user: User (FK)
├─ currency_pair: CharField (e.g., "EURUSD")
├─ trade_type: buy, sell
├─ position_size: Decimal (in base currency)
├─ leverage: Integer
├─ entry_price: Decimal
├─ current_price: Decimal (updated in real-time)
├─ exit_price: Decimal (nullable, when closed)
├─ stop_loss: Decimal (nullable)
├─ take_profit: Decimal (nullable)
├─ opened_at: DateTime
├─ closed_at: DateTime (nullable)
├─ status: open, closed, stopped_out, take_profit_hit
├─ profit_loss: Decimal
├─ profit_loss_percentage: Float
├─ commission: Decimal (simulated)
├─ swap_fee: Decimal (simulated overnight fee)
├─ notes: TextField (user's trade notes)
├─ strategy_used: TradingStrategy (FK, nullable)
└─ signal_followed: TradingSignal (FK, nullable)

TradeHistory
├─ id (PK)
├─ trade: Trade (FK)
├─ price: Decimal
├─ timestamp: DateTime
├─ event_type: price_update, stop_loss_adjusted, take_profit_adjusted
└─ notes: CharField (nullable)
```

### Strategy & Analysis
```
TradingStrategy
├─ id (PK)
├─ user: User (FK, nullable if system strategy)
├─ name: CharField
├─ description: TextField
├─ strategy_type: scalping, day_trading, swing_trading, position_trading
├─ indicators_used: JSONField (MA, RSI, MACD, Bollinger, etc.)
├─ entry_rules: JSONField
├─ exit_rules: JSONField
├─ risk_management: JSONField (risk per trade, max drawdown, etc.)
├─ currency_pairs: JSONField (applicable pairs)
├─ timeframe: M1, M5, M15, M30, H1, H4, D1
├─ backtest_results: JSONField (nullable)
├─ win_rate: Float (from backtest or live trades)
├─ is_public: Boolean (shareable)
├─ followers_count: Integer
├─ rating: Float
├─ created_at, updated_at
└─ is_system_strategy: Boolean

StrategyPerformance
├─ id (PK)
├─ strategy: TradingStrategy (FK)
├─ period_start: Date
├─ period_end: Date
├─ total_trades: Integer
├─ winning_trades: Integer
├─ losing_trades: Integer
├─ total_profit_loss: Decimal
├─ win_rate: Float
├─ average_profit: Decimal
├─ average_loss: Decimal
├─ profit_factor: Float
├─ sharpe_ratio: Float
├─ max_drawdown: Decimal
└─ calculated_at: DateTime
```

### Signals & Community
```
TradingSignal
├─ id (PK)
├─ provider: User (FK, pro trader providing signal)
├─ currency_pair: CharField
├─ signal_type: buy, sell
├─ entry_price: Decimal
├─ stop_loss: Decimal
├─ take_profit_1: Decimal
├─ take_profit_2: Decimal (nullable)
├─ take_profit_3: Decimal (nullable)
├─ confidence_level: Integer (1-10)
├─ reasoning: TextField
├─ timeframe: M5, M15, H1, H4, D1
├─ status: pending, active, closed_profit, closed_loss, cancelled
├─ opened_at: DateTime
├─ closed_at: DateTime (nullable)
├─ actual_outcome: Decimal (nullable, profit/loss)
├─ followers_count: Integer (how many used this signal)
├─ success_rate: Float (among followers)
├─ is_premium: Boolean (requires paid subscription)
└─ expires_at: DateTime

SignalFollow
├─ id (PK)
├─ signal: TradingSignal (FK)
├─ user: User (FK)
├─ trade: Trade (FK, nullable, if user executed)
├─ followed_at: DateTime
├─ outcome: profit, loss, pending
└─ user_rating: Integer (1-5, user rates signal quality)

CommunityPost
├─ id (PK)
├─ author: User (FK)
├─ post_type: analysis, question, achievement, strategy_share
├─ title: CharField
├─ content: TextField
├─ currency_pairs: JSONField (nullable)
├─ images: JSONField (list of image URLs, nullable)
├─ related_trade: Trade (FK, nullable)
├─ related_strategy: TradingStrategy (FK, nullable)
├─ likes_count: Integer
├─ comments_count: Integer
├─ views_count: Integer
├─ is_pinned: Boolean
├─ created_at, updated_at
└─ edited_at: DateTime (nullable)

PostComment
├─ id (PK)
├─ post: CommunityPost (FK)
├─ author: User (FK)
├─ content: TextField
├─ parent_comment: Self (FK, nullable, for nested replies)
├─ likes_count: Integer
└─ created_at

PostLike
├─ id (PK)
├─ post: CommunityPost (FK, nullable)
├─ comment: PostComment (FK, nullable)
├─ user: User (FK)
└─ created_at

Leaderboard
├─ id (PK)
├─ period_type: daily, weekly, monthly, all_time
├─ period_start: Date
├─ period_end: Date
├─ user: User (FK)
├─ rank: Integer
├─ total_profit_loss: Decimal
├─ win_rate: Float
├─ total_trades: Integer
├─ roi_percentage: Float
└─ calculated_at: DateTime
```

---

## Updated Subscription Plans

```python
SUBSCRIPTION_PLANS = {
    # Teacher Plans
    'teacher_free': {
        'price': 0,
        'max_students': 30,
        'max_assignments': 10,
        'ai_lesson_plans': 3,  # per month
        'worksheet_generation': 5,  # per month
    },
    'teacher_pro': {
        'price': 9.99,  # monthly
        'max_students': 100,
        'max_assignments': -1,  # unlimited
        'ai_lesson_plans': -1,
        'worksheet_generation': -1,
        'advanced_analytics': True,
        'parent_notifications': True,
    },
    'school': {
        'price': 99,  # yearly
        'max_teachers': -1,
        'max_students': -1,
        'shared_resources': True,
        'admin_dashboard': True,
        'custom_branding': True,
    },
    'district': {
        'price': 999,  # yearly
        'max_schools': -1,
        'district_analytics': True,
        'api_access': True,
        'dedicated_support': True,
    },

    # Remittance Plans
    'remittance_free': {
        'price': 0,
        'max_alerts': 1,
        'comparison_history_days': 30,
        'ai_predictions': False,
    },
    'remittance_pro': {
        'price': 4.99,  # monthly
        'max_alerts': -1,
        'comparison_history_days': -1,
        'ai_predictions': True,
        'sms_notifications': True,
        'priority_support': True,
    },

    # Trading Plans
    'trader_free': {
        'price': 0,
        'max_virtual_portfolios': 1,
        'max_open_trades': 5,
        'historical_data_days': 30,
        'basic_indicators': True,
        'premium_signals': False,
    },
    'trader_pro': {
        'price': 29,  # monthly
        'max_virtual_portfolios': 5,
        'max_open_trades': 50,
        'historical_data_days': 365,
        'advanced_indicators': True,
        'premium_signals': True,
        'strategy_backtesting': True,
        'real_time_data': True,
    },
    'trader_premium': {
        'price': 99,  # monthly
        'max_virtual_portfolios': -1,
        'max_open_trades': -1,
        'historical_data_days': -1,
        'all_features': True,
        'auto_trading_bot': True,
        'dedicated_analyst': True,
        'api_access': True,
    },
}
```

---

## Database Relationships Summary

```
User (1) ─── (1) UserProfile
     │
     ├─ (1) ─── (1) Subscription ─── (1) SubscriptionPlan
     │
     ├─ (1) ─── (*) UsageStatistics
     ├─ (1) ─── (*) LearningProgress
     ├─ (1) ─── (*) UserAchievement ─── (1) Achievement
     │
     # Teacher relationships
     ├─ (1) ─── (*) ClassroomGroup (as teacher)
     ├─ (*) ─── (*) ClassroomGroup (as student)
     ├─ (1) ─── (*) Assignment (as teacher)
     ├─ (1) ─── (*) StudentSubmission (as student)
     ├─ (1) ─── (*) LessonPlan
     ├─ (1) ─── (*) Worksheet
     │
     # Remittance relationships
     ├─ (1) ─── (*) ExchangeRateAlert
     ├─ (1) ─── (*) RemittanceHistory
     ├─ (1) ─── (*) RemittanceComparison
     ├─ (1) ─── (*) RemittanceGroup (as admin)
     ├─ (*) ─── (*) RemittanceGroup (as member)
     │
     # Trading relationships
     ├─ (1) ─── (*) VirtualPortfolio
     ├─ (1) ─── (*) Trade
     ├─ (1) ─── (*) TradingStrategy
     ├─ (1) ─── (*) TradingSignal (as provider)
     ├─ (1) ─── (*) SignalFollow (as follower)
     ├─ (1) ─── (*) CommunityPost
     └─ (1) ─── (*) Leaderboard
```

---

## Indexes & Performance Optimization

### Critical Indexes
```python
# Teacher models
Assignment: ['classroom', 'teacher', 'due_date', 'is_published']
StudentSubmission: ['assignment', 'student', 'status', 'submitted_at']

# Remittance models
ExchangeRateAlert: ['user', 'is_active', 'from_currency', 'to_currency']
RemittanceHistory: ['user', 'transfer_date', 'status']

# Trading models
Trade: ['portfolio', 'user', 'status', 'opened_at']
TradingSignal: ['provider', 'status', 'is_premium', 'opened_at']
Leaderboard: ['period_type', 'period_start', 'rank']

# Common indexes
LearningProgress: ['user', 'timestamp']
UsageStatistics: ['user', 'feature', 'date'] (already unique_together)
```

---

## Migration Strategy

### Phase 1 Implementation (Week 1-2)
1. Add new roles to UserProfile
2. Create Assignment-related models
3. Create LessonPlan and Worksheet models
4. Create CurriculumStandard
5. Extend ClassroomGroup

### Phase 2 Implementation (Week 3-4)
1. Create ExchangeRateAlert
2. Create RemittanceProvider and RemittanceFee
3. Create RemittanceHistory and RemittanceGroup
4. Create RatePrediction

### Phase 3 Implementation (Week 5-8)
1. Create VirtualPortfolio and Trade
2. Create TradingStrategy and StrategyPerformance
3. Create TradingSignal and SignalFollow
4. Create CommunityPost and related models
5. Create Leaderboard

---

## Next Steps

1. Review this design document
2. Make any necessary adjustments
3. Implement models phase by phase
4. Create migrations
5. Build admin interface
6. Create API endpoints
7. Build frontend UI

---

**Questions to consider:**
- Should we add soft-delete (is_deleted field) to critical models?
- Do we need audit logs for financial transactions?
- Should we implement versioning for assignments/lesson plans?
- Real-time data requirements for trading features?
