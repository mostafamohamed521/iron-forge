"""
Test suite for IronForge Gym Platform.
Run with: python manage.py test tests
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta

from apps.users.models import CustomUser, ProgressEntry
from apps.memberships.models import MembershipPlan, UserMembership
from apps.workouts.models import WorkoutProgram, Exercise, MuscleGroup
from apps.bookings.models import TrainingSession, Booking


# ── Factories ────────────────────────────────────────────────────────────────

def make_user(email='test@example.com', password='testpass123', **kwargs):
    return CustomUser.objects.create_user(
        username=email, email=email, password=password,
        first_name='Test', last_name='User', **kwargs
    )

def make_plan(name='premium', price=59):
    display = {'basic':'Basic','premium':'Premium','vip':'VIP'}.get(name, name.title())
    return MembershipPlan.objects.get_or_create(
        name=name,
        defaults={
            'display_name': display,
            'description': 'Test plan',
            'price': price,
            'duration_days': 30,
            'features': ['Feature A', 'Feature B'],
        }
    )[0]

def make_membership(user, plan=None, days=30):
    if plan is None:
        plan = make_plan()
    return UserMembership.objects.create(
        user=user, plan=plan,
        start_date=timezone.now().date(),
        end_date=timezone.now().date() + timedelta(days=days),
        status='active', is_active=True,
    )


# ── User Model Tests ──────────────────────────────────────────────────────────

class CustomUserModelTest(TestCase):

    def test_create_user(self):
        user = make_user()
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)

    def test_get_full_name(self):
        user = make_user()
        self.assertEqual(user.get_full_name(), 'Test User')

    def test_bmi_calculation(self):
        user = make_user()
        user.height_cm = 175
        user.weight_kg = 70
        self.assertAlmostEqual(user.bmi, 22.9, places=0)

    def test_bmi_none_when_missing(self):
        user = make_user()
        self.assertIsNone(user.bmi)

    def test_active_membership_none(self):
        user = make_user()
        self.assertIsNone(user.active_membership)

    def test_active_membership_present(self):
        user = make_user()
        membership = make_membership(user)
        self.assertEqual(user.active_membership, membership)


# ── Membership Tests ──────────────────────────────────────────────────────────

class MembershipPlanModelTest(TestCase):

    def test_plan_creation(self):
        plan = make_plan('basic', 29)
        self.assertEqual(plan.name, 'basic')
        self.assertEqual(plan.price, 29)

    def test_plan_str(self):
        plan = make_plan()
        self.assertIn('Premium', str(plan))


class UserMembershipModelTest(TestCase):

    def setUp(self):
        self.user = make_user()
        self.plan = make_plan()

    def test_days_remaining(self):
        m = make_membership(self.user, self.plan, days=30)
        self.assertGreater(m.days_remaining, 0)
        self.assertLessEqual(m.days_remaining, 30)

    def test_expired_membership(self):
        m = UserMembership.objects.create(
            user=self.user, plan=self.plan,
            start_date=timezone.now().date() - timedelta(days=40),
            end_date=timezone.now().date() - timedelta(days=10),
            status='active', is_active=True,
        )
        self.assertTrue(m.is_expired)


# ── Workout Tests ─────────────────────────────────────────────────────────────

class WorkoutProgramModelTest(TestCase):

    def setUp(self):
        self.trainer = make_user('trainer@example.com', is_trainer=True)

    def test_create_program(self):
        program = WorkoutProgram.objects.create(
            title='Beginner Gains',
            description='Start here.',
            goal='muscle_gain',
            level='beginner',
            duration_weeks=4,
            days_per_week=3,
            created_by=self.trainer,
        )
        self.assertEqual(str(program), 'Beginner Gains (Beginner)')

    def test_exercise_creation(self):
        mg = MuscleGroup.objects.create(name='Chest')
        ex = Exercise.objects.create(
            name='Bench Press', description='', instructions='',
            difficulty='intermediate', equipment='barbell',
        )
        ex.muscle_groups.add(mg)
        self.assertIn(mg, ex.muscle_groups.all())


# ── Booking Tests ─────────────────────────────────────────────────────────────

class BookingModelTest(TestCase):

    def setUp(self):
        self.trainer = make_user('trainer@test.com', is_trainer=True)
        self.member  = make_user('member@test.com')
        self.plan = make_plan()
        make_membership(self.member, self.plan)
        self.session = TrainingSession.objects.create(
            trainer=self.trainer,
            title='Morning HIIT',
            session_type='group',
            date=timezone.now().date() + timedelta(days=3),
            start_time='07:00',
            end_time='08:00',
            max_participants=10,
            price=0,
        )

    def test_session_is_available(self):
        self.assertTrue(self.session.is_available)

    def test_booking_creation(self):
        booking = Booking.objects.create(
            user=self.member,
            session=self.session,
            status='confirmed',
        )
        self.assertEqual(booking.status, 'confirmed')

    def test_cancel_booking(self):
        booking = Booking.objects.create(
            user=self.member,
            session=self.session,
            status='confirmed',
        )
        booking.cancel()
        self.assertEqual(booking.status, 'cancelled')


# ── View Tests ────────────────────────────────────────────────────────────────

class LandingViewTest(TestCase):

    def test_landing_page_loads(self):
        response = self.client.get(reverse('landing'))
        self.assertEqual(response.status_code, 200)

    def test_landing_redirects_authenticated_user(self):
        user = make_user()
        self.client.force_login(user)
        response = self.client.get(reverse('landing'))
        self.assertRedirects(response, reverse('dashboard'))


class DashboardViewTest(TestCase):

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(response, '/auth/login/?next=/dashboard/')

    def test_dashboard_loads_for_member(self):
        user = make_user()
        self.client.force_login(user)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, user.first_name)


class MembershipPlansViewTest(TestCase):

    def setUp(self):
        make_plan('basic', 29)
        make_plan('premium', 59)

    def test_plans_page_loads(self):
        response = self.client.get(reverse('membership_plans'))
        self.assertEqual(response.status_code, 200)

    def test_plans_listed(self):
        response = self.client.get(reverse('membership_plans'))
        self.assertContains(response, 'BASIC')
        self.assertContains(response, 'PREMIUM')


class WorkoutsViewTest(TestCase):

    def test_workouts_page_loads(self):
        response = self.client.get(reverse('workouts'))
        self.assertEqual(response.status_code, 200)


class BookingsViewTest(TestCase):

    def test_sessions_page_loads(self):
        response = self.client.get(reverse('sessions'))
        self.assertEqual(response.status_code, 200)

    def test_book_session_requires_login(self):
        trainer = make_user('t@t.com', is_trainer=True)
        session = TrainingSession.objects.create(
            trainer=trainer, title='Test',
            session_type='personal',
            date=timezone.now().date() + timedelta(days=1),
            start_time='10:00', end_time='11:00',
            max_participants=1, price=0,
        )
        response = self.client.get(reverse('book_session', args=[session.id]))
        self.assertEqual(response.status_code, 302)


# ── API Tests ─────────────────────────────────────────────────────────────────

class UserAPITest(TestCase):

    def setUp(self):
        self.user = make_user()
        self.client = Client()

    def test_profile_api_requires_auth(self):
        response = self.client.get('/api/v1/users/profile/')
        self.assertEqual(response.status_code, 403)

    def test_profile_api_authenticated(self):
        self.client.force_login(self.user)
        response = self.client.get('/api/v1/users/profile/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['email'], self.user.email)


class MembershipsAPITest(TestCase):

    def test_plans_api_public(self):
        make_plan('basic', 29)
        response = self.client.get('/api/v1/memberships/plans/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
