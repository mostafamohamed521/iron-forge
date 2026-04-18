# 🏋️ IRONFORGE — Enterprise Gym Platform

A production-ready, full-stack Django gym & fitness SaaS platform.

---

## 📁 Project Structure

```
gymplatform/
├── config/
│   ├── __init__.py
│   ├── settings.py          # All Django settings
│   ├── urls.py              # Root URL configuration
│   └── wsgi.py
├── apps/
│   ├── users/               # Custom user, profiles, progress tracking
│   ├── memberships/         # Plans, subscriptions, gym classes
│   ├── workouts/            # Programs, exercises, workout logging
│   ├── diet/                # Diet plans, food library, food logging
│   ├── bookings/            # Training sessions, booking management
│   └── payments/            # Stripe integration, payment history
├── templates/
│   ├── base.html            # Base layout with navbar + footer
│   ├── landing.html         # Public homepage
│   ├── users/               # Dashboard, profile, trainers
│   ├── memberships/         # Plans listing, my membership
│   ├── workouts/            # Programs list + detail
│   ├── bookings/            # Sessions list, my bookings
│   ├── payments/            # Checkout, history
│   └── admin/               # Custom analytics dashboard
├── static/
│   ├── css/main.css         # Full design system (dark theme)
│   └── js/main.js           # Navbar, animations, helpers
├── tests/
│   └── test_platform.py     # 20+ unit + integration tests
├── .env.example
├── requirements.txt
├── manage.py
├── Procfile                 # Render / Heroku
└── render.yaml              # Render.com auto-deploy config
```

---

## ⚡ Local Setup (5 minutes)

### 1. Clone & enter directory
```bash
git clone https://github.com/yourusername/ironforge-gym.git
cd gymplatform
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment
```bash
cp .env.example .env
# Edit .env — set SECRET_KEY, DATABASE_URL, Stripe keys, email
```

Minimal `.env` for local dev:
```env
SECRET_KEY=any-random-string-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

### 5. Run migrations
```bash
python manage.py migrate
```

### 6. Create superuser (admin)
```bash
python manage.py createsuperuser
```

### 7. Load sample data (optional)
```bash
python manage.py shell -c "
from apps.memberships.models import MembershipPlan
MembershipPlan.objects.get_or_create(name='basic', defaults={'display_name':'Basic','description':'Get started','price':29,'duration_days':30,'features':['Gym floor access','Locker room','Basic equipment','2 classes/month']})
MembershipPlan.objects.get_or_create(name='premium', defaults={'display_name':'Premium','description':'Most popular','price':59,'duration_days':30,'features':['All Basic features','Unlimited classes','Personal trainer 2x/month','Nutrition consult','Pool & sauna']})
MembershipPlan.objects.get_or_create(name='vip', defaults={'display_name':'VIP','description':'Ultimate elite','price':99,'duration_days':30,'features':['All Premium features','Dedicated trainer','Custom meal plans','Priority booking','24/7 access','Guest passes']})
print('Plans created!')
"
```

### 8. Collect static files
```bash
python manage.py collectstatic
```

### 9. Start development server
```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000**

---

## 🧪 Running Tests

```bash
python manage.py test tests
```

With coverage:
```bash
coverage run manage.py test tests
coverage report
coverage html   # Open htmlcov/index.html
```

---

## 🔐 Security Checklist

| Feature | Implementation |
|---|---|
| CSRF Protection | Django middleware (enabled by default) |
| XSS Protection | Django template auto-escaping |
| SQL Injection | Django ORM (no raw queries) |
| Brute-force protection | django-allauth login attempt limits |
| Password validation | Django AUTH_PASSWORD_VALIDATORS |
| Secure file uploads | Type & size validation in views |
| Security headers | Custom SecurityHeadersMiddleware |
| HTTPS enforcement | `SECURE_SSL_REDIRECT=True` in prod |
| Secure cookies | `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE` |
| HSTS | `SECURE_HSTS_SECONDS=31536000` |
| Clickjacking | `X_FRAME_OPTIONS=DENY` |

---

## 🌐 Deploy FREE on Render.com

### Option A — Auto-deploy via render.yaml (Easiest)

1. Push project to GitHub
2. Go to https://render.com → New → Blueprint
3. Connect your GitHub repo
4. Render reads `render.yaml` and sets everything up automatically
5. Your app will be live at `https://ironforge-gym.onrender.com`

### Option B — Manual Render Setup

1. **New Web Service** → Connect GitHub repo
2. Settings:
   - **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
   - **Start Command:** `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`
3. **Environment Variables** (add in Render dashboard):
   ```
   SECRET_KEY        = (generate random 50-char string)
   DEBUG             = False
   ALLOWED_HOSTS     = .onrender.com
   DATABASE_URL      = (Render provides this from PostgreSQL add-on)
   EMAIL_BACKEND     = django.core.mail.backends.console.EmailBackend
   STRIPE_PUBLIC_KEY = pk_live_...
   STRIPE_SECRET_KEY = sk_live_...
   ```
4. Add **PostgreSQL** database from Render dashboard → copy connection string to `DATABASE_URL`
5. Click **Deploy** → Your URL: `https://your-app.onrender.com`

---

## 💳 Stripe Setup

1. Sign up at https://stripe.com
2. Get test keys from Dashboard → Developers → API Keys
3. Add to `.env`:
   ```
   STRIPE_PUBLIC_KEY=pk_test_xxxxx
   STRIPE_SECRET_KEY=sk_test_xxxxx
   ```
4. For webhooks (local testing):
   ```bash
   # Install Stripe CLI
   stripe listen --forward-to localhost:8000/payments/webhook/
   # Copy webhook secret → STRIPE_WEBHOOK_SECRET=whsec_xxx
   ```

---

## 📧 Email Setup (Gmail)

1. Enable 2FA on your Google account
2. Generate App Password: Google Account → Security → App passwords
3. Add to `.env`:
   ```
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   ```

---

## 🏗️ Adding Data via Admin

1. Go to `/admin/` and login as superuser
2. **Memberships → Membership Plans** — Add Basic / Premium / VIP
3. **Workouts → Workout Programs** — Add programs with workout days and sets
4. **Diet → Diet Plans** — Add nutrition plans with meals
5. **Bookings → Training Sessions** — Create bookable sessions
6. **Users → Custom Users** — Mark users as trainers (`is_trainer=True`)

---

## 🔌 REST API Endpoints

| Endpoint | Method | Auth | Description |
|---|---|---|---|
| `/api/v1/users/profile/` | GET, PATCH | ✅ | User profile |
| `/api/v1/users/progress/` | GET, POST | ✅ | Progress entries |
| `/api/v1/memberships/plans/` | GET | ❌ | All active plans |
| `/api/v1/memberships/my/` | GET | ✅ | User's membership |
| `/api/v1/workouts/` | GET | ❌ | All programs |
| `/api/v1/workouts/logs/` | GET, POST | ✅ | Workout logs |
| `/api/v1/diet/` | GET | ❌ | All diet plans |
| `/api/v1/diet/logs/` | GET, POST | ✅ | Food logs |
| `/api/v1/bookings/sessions/` | GET | ❌ | Available sessions |
| `/api/v1/bookings/` | GET, POST | ✅ | User's bookings |

---

## 🤖 Extending with AI (Optional)

To add an AI personal trainer powered by Claude:

```python
# In any view:
import anthropic

client = anthropic.Anthropic(api_key="your-key")

def ai_trainer_advice(user_profile, question):
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": f"User profile: {user_profile}\n\nQuestion: {question}"
        }],
        system="You are an expert personal trainer. Give personalized, safe fitness advice."
    )
    return message.content[0].text
```

---

## 📊 Tech Stack Summary

| Layer | Technology |
|---|---|
| Backend | Django 5.0, Django REST Framework |
| Database | PostgreSQL (prod) / SQLite (dev) |
| Auth | django-allauth (email + social) |
| Payments | Stripe (PaymentIntents API) |
| Frontend | HTML5, CSS3 (custom design system), Vanilla JS |
| Fonts | Bebas Neue (display), DM Sans (body) |
| Icons | Bootstrap Icons |
| Charts | Chart.js |
| Deployment | Render.com (free tier) |
| Static files | WhiteNoise |
| Image processing | Pillow |

---

## 🛣️ Roadmap / What to Build Next

- [ ] 📱 Mobile app (React Native / Flutter)  
- [ ] 🤖 AI personal trainer chatbot (Claude API)  
- [ ] 📊 Advanced analytics dashboard with charts  
- [ ] 📹 Video workout player  
- [ ] 🏆 Gamification (achievements, leaderboards)  
- [ ] 👥 Social features (following, challenges)  
- [ ] 📲 Push notifications  
- [ ] 🌍 Multi-language support  

---

Built with ❤️ using Django + IronForge Design System.
