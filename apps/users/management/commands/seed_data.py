"""
Management command: python manage.py seed_data
Seeds the database with realistic sample data for development/demo.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Seed the database with realistic sample data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('\n🌱 Seeding IronForge database...\n'))
        self._seed_plans()
        self._seed_muscle_groups()
        self._seed_exercises()
        self._seed_food_items()
        self._seed_trainers()
        self._seed_members()
        self._seed_workout_programs()
        self._seed_diet_plans()
        self._seed_sessions()
        self._seed_bookings()
        self._seed_admin()
        self.stdout.write(self.style.SUCCESS('\n✅ Seeding complete!\n'))
        self._print_summary()

    # ── Plans ────────────────────────────────────────────────────────────────
    def _seed_plans(self):
        from apps.memberships.models import MembershipPlan
        plans = [
            {
                'name': 'basic', 'display_name': 'Basic', 'price': 29.00,
                'duration_days': 30, 'billing_cycle': 'monthly',
                'description': 'Perfect for beginners getting started on their fitness journey.',
                'features': [
                    'Full gym floor access',
                    'Locker room & showers',
                    'Basic cardio equipment',
                    '2 group classes per month',
                    'Fitness assessment on signup',
                ],
            },
            {
                'name': 'premium', 'display_name': 'Premium', 'price': 59.00,
                'duration_days': 30, 'billing_cycle': 'monthly',
                'description': 'Our most popular plan with unlimited classes and trainer access.',
                'features': [
                    'Everything in Basic',
                    'Unlimited group classes',
                    'Personal trainer (2 sessions/month)',
                    'Nutrition consultation',
                    'Pool, sauna & steam room',
                    'Guest passes (1/month)',
                    'Priority session booking',
                ],
            },
            {
                'name': 'vip', 'display_name': 'VIP', 'price': 99.00,
                'duration_days': 30, 'billing_cycle': 'monthly',
                'description': 'The ultimate elite experience with dedicated personal coaching.',
                'features': [
                    'Everything in Premium',
                    'Dedicated personal trainer',
                    'Custom weekly meal plans',
                    'Unlimited guest passes (2/month)',
                    '24/7 gym access',
                    'Private locker',
                    'Monthly body composition scan',
                    'Recovery room access',
                ],
            },
        ]
        for p in plans:
            obj, created = MembershipPlan.objects.update_or_create(
                name=p['name'], defaults=p
            )
            status = 'Created' if created else 'Updated'
            self.stdout.write(f'  {status} plan: {obj.display_name}')

    # ── Muscle Groups ────────────────────────────────────────────────────────
    def _seed_muscle_groups(self):
        from apps.workouts.models import MuscleGroup
        groups = ['Chest', 'Back', 'Shoulders', 'Biceps', 'Triceps',
                  'Quadriceps', 'Hamstrings', 'Glutes', 'Calves', 'Core', 'Forearms']
        for name in groups:
            MuscleGroup.objects.get_or_create(name=name)
        self.stdout.write(f'  Created {len(groups)} muscle groups')

    # ── Exercises ────────────────────────────────────────────────────────────
    def _seed_exercises(self):
        from apps.workouts.models import Exercise, MuscleGroup
        exercises = [
            # Chest
            {'name': 'Barbell Bench Press', 'difficulty': 'intermediate', 'equipment': 'barbell',
             'muscles': ['Chest', 'Triceps', 'Shoulders'],
             'description': 'The king of chest exercises. Builds mass and strength in the pectorals.',
             'instructions': '1. Lie flat on bench\n2. Grip bar slightly wider than shoulder width\n3. Lower bar to chest\n4. Press back up explosively\n5. Keep core tight throughout'},
            {'name': 'Incline Dumbbell Press', 'difficulty': 'intermediate', 'equipment': 'dumbbells',
             'muscles': ['Chest', 'Shoulders'],
             'description': 'Targets the upper chest for a full, rounded appearance.',
             'instructions': '1. Set bench to 30-45 degrees\n2. Hold dumbbells at chest height\n3. Press up and slightly inward\n4. Lower with control'},
            {'name': 'Push-Up', 'difficulty': 'beginner', 'equipment': 'bodyweight',
             'muscles': ['Chest', 'Triceps', 'Core'],
             'description': 'The foundational bodyweight chest exercise.',
             'instructions': '1. Hands shoulder-width apart\n2. Body straight from head to heels\n3. Lower until chest nearly touches floor\n4. Push back to start'},
            # Back
            {'name': 'Pull-Up', 'difficulty': 'intermediate', 'equipment': 'bodyweight',
             'muscles': ['Back', 'Biceps'],
             'description': 'Best compound exercise for building a wide back.',
             'instructions': '1. Grip bar wider than shoulder width\n2. Hang with arms fully extended\n3. Pull until chin clears bar\n4. Lower slowly'},
            {'name': 'Barbell Deadlift', 'difficulty': 'advanced', 'equipment': 'barbell',
             'muscles': ['Back', 'Hamstrings', 'Glutes', 'Core'],
             'description': 'The ultimate full-body strength builder.',
             'instructions': '1. Bar over mid-foot\n2. Hip-width stance\n3. Hinge at hips, grip bar\n4. Drive through heels\n5. Lock out hips and knees'},
            {'name': 'Dumbbell Row', 'difficulty': 'beginner', 'equipment': 'dumbbells',
             'muscles': ['Back', 'Biceps'],
             'description': 'Great unilateral exercise for back thickness.',
             'instructions': '1. Plant one hand and knee on bench\n2. Hold dumbbell in other hand\n3. Pull elbow to hip\n4. Lower with control'},
            # Shoulders
            {'name': 'Overhead Press', 'difficulty': 'intermediate', 'equipment': 'barbell',
             'muscles': ['Shoulders', 'Triceps', 'Core'],
             'description': 'The best shoulder mass builder.',
             'instructions': '1. Bar at upper chest\n2. Press overhead until arms locked\n3. Lower under control\n4. Keep core braced'},
            {'name': 'Lateral Raise', 'difficulty': 'beginner', 'equipment': 'dumbbells',
             'muscles': ['Shoulders'],
             'description': 'Isolates the medial deltoid for shoulder width.',
             'instructions': '1. Stand with dumbbells at sides\n2. Raise arms to shoulder height\n3. Pause briefly\n4. Lower slowly'},
            # Arms
            {'name': 'Barbell Curl', 'difficulty': 'beginner', 'equipment': 'barbell',
             'muscles': ['Biceps', 'Forearms'],
             'description': 'Classic mass builder for the biceps.',
             'instructions': '1. Stand with barbell at thighs\n2. Curl up to shoulders\n3. Squeeze at top\n4. Lower slowly'},
            {'name': 'Tricep Dips', 'difficulty': 'intermediate', 'equipment': 'bodyweight',
             'muscles': ['Triceps', 'Chest'],
             'description': 'Compound movement for tricep size and strength.',
             'instructions': '1. Grip parallel bars\n2. Lower body until elbows at 90°\n3. Push back up\n4. Keep torso slightly forward'},
            {'name': 'Skull Crushers', 'difficulty': 'intermediate', 'equipment': 'barbell',
             'muscles': ['Triceps'],
             'description': 'Top isolation exercise for tricep mass.',
             'instructions': '1. Lie on bench with barbell\n2. Lower bar toward forehead\n3. Keep elbows fixed\n4. Extend back to start'},
            # Legs
            {'name': 'Barbell Squat', 'difficulty': 'intermediate', 'equipment': 'barbell',
             'muscles': ['Quadriceps', 'Glutes', 'Hamstrings', 'Core'],
             'description': 'The king of all exercises. Builds total lower body mass.',
             'instructions': '1. Bar on upper traps\n2. Feet shoulder-width\n3. Squat to parallel\n4. Drive up through heels'},
            {'name': 'Romanian Deadlift', 'difficulty': 'intermediate', 'equipment': 'barbell',
             'muscles': ['Hamstrings', 'Glutes', 'Back'],
             'description': 'The best exercise for hamstring development.',
             'instructions': '1. Hold bar at hips\n2. Hinge forward keeping back flat\n3. Feel stretch in hamstrings\n4. Drive hips forward to return'},
            {'name': 'Leg Press', 'difficulty': 'beginner', 'equipment': 'machine',
             'muscles': ['Quadriceps', 'Glutes'],
             'description': 'Safe compound movement for leg volume.',
             'instructions': '1. Seat with back flat\n2. Feet shoulder-width on platform\n3. Lower until 90° knee angle\n4. Press back up'},
            {'name': 'Calf Raise', 'difficulty': 'beginner', 'equipment': 'machine',
             'muscles': ['Calves'],
             'description': 'Isolates the gastrocnemius and soleus.',
             'instructions': '1. Stand on edge of platform\n2. Rise up on toes\n3. Hold at top\n4. Lower heel below platform'},
            # Core
            {'name': 'Plank', 'difficulty': 'beginner', 'equipment': 'bodyweight',
             'muscles': ['Core'],
             'description': 'Foundational isometric core exercise.',
             'instructions': '1. Forearms on floor\n2. Body in straight line\n3. Hold position\n4. Breathe normally'},
            {'name': 'Cable Crunch', 'difficulty': 'beginner', 'equipment': 'cable',
             'muscles': ['Core'],
             'description': 'Weighted ab exercise for core development.',
             'instructions': '1. Kneel facing cable\n2. Hold rope at head\n3. Crunch down\n4. Squeeze abs at bottom'},
            # Cardio
            {'name': 'Kettlebell Swing', 'difficulty': 'intermediate', 'equipment': 'kettlebell',
             'muscles': ['Glutes', 'Hamstrings', 'Core', 'Shoulders'],
             'description': 'Explosive full-body cardio and strength exercise.',
             'instructions': '1. Hinge at hips\n2. Swing kettlebell back between legs\n3. Explosively drive hips forward\n4. Let kettlebell float to shoulder height'},
        ]
        count = 0
        for ex_data in exercises:
            muscles = ex_data.pop('muscles')
            ex, created = Exercise.objects.update_or_create(
                name=ex_data['name'],
                defaults={**ex_data, 'calories_per_minute': random.uniform(4, 10)}
            )
            for muscle_name in muscles:
                mg = MuscleGroup.objects.get(name=muscle_name)
                ex.muscle_groups.add(mg)
            if created:
                count += 1
        self.stdout.write(f'  Created {count} exercises')

    # ── Food Items ───────────────────────────────────────────────────────────
    def _seed_food_items(self):
        from apps.diet.models import FoodItem
        foods = [
            # Protein
            ('Chicken Breast (grilled)', 'protein', 165, 31, 0, 3.6, 0),
            ('Eggs (whole)', 'protein', 155, 13, 1.1, 11, 0),
            ('Tuna (canned in water)', 'protein', 116, 26, 0, 1, 0),
            ('Whey Protein Powder', 'protein', 120, 25, 3, 1.5, 0),
            ('Greek Yogurt (0% fat)', 'protein', 59, 10, 3.6, 0.4, 0),
            ('Salmon (baked)', 'protein', 208, 20, 0, 13, 0),
            ('Cottage Cheese', 'protein', 98, 11, 3.4, 4.3, 0),
            # Carbs
            ('Brown Rice (cooked)', 'carbs', 112, 2.3, 24, 0.9, 1.8),
            ('Sweet Potato (baked)', 'carbs', 86, 1.6, 20, 0.1, 3),
            ('Oatmeal (dry)', 'carbs', 389, 17, 66, 7, 11),
            ('Whole Wheat Bread', 'carbs', 247, 13, 41, 4, 7),
            ('White Rice (cooked)', 'carbs', 130, 2.7, 28, 0.3, 0.4),
            ('Quinoa (cooked)', 'carbs', 120, 4.4, 21, 1.9, 2.8),
            # Fats
            ('Avocado', 'fat', 160, 2, 9, 15, 7),
            ('Almonds', 'fat', 579, 21, 22, 50, 13),
            ('Olive Oil', 'fat', 884, 0, 0, 100, 0),
            ('Peanut Butter (natural)', 'fat', 588, 25, 20, 50, 6),
            # Vegetables
            ('Broccoli (steamed)', 'vegetable', 34, 2.8, 6.6, 0.4, 2.6),
            ('Spinach (raw)', 'vegetable', 23, 2.9, 3.6, 0.4, 2.2),
            ('Mixed Salad Greens', 'vegetable', 20, 1.8, 3.2, 0.3, 2),
            ('Bell Pepper (red)', 'vegetable', 31, 1, 6, 0.3, 2.1),
            ('Cucumber', 'vegetable', 16, 0.7, 3.6, 0.1, 0.5),
            # Fruits
            ('Banana', 'fruit', 89, 1.1, 23, 0.3, 2.6),
            ('Apple', 'fruit', 52, 0.3, 14, 0.2, 2.4),
            ('Blueberries', 'fruit', 57, 0.7, 14, 0.3, 2.4),
            ('Orange', 'fruit', 47, 0.9, 12, 0.1, 2.4),
            # Dairy
            ('Skim Milk', 'dairy', 35, 3.4, 5, 0.1, 0),
            ('Low-fat Cheese', 'dairy', 175, 25, 3, 7, 0),
        ]
        count = 0
        for name, cat, cal, prot, carb, fat, fiber in foods:
            _, created = FoodItem.objects.update_or_create(
                name=name,
                defaults={
                    'category': cat, 'calories_per_100g': cal,
                    'protein_per_100g': prot, 'carbs_per_100g': carb,
                    'fat_per_100g': fat, 'fiber_per_100g': fiber,
                }
            )
            if created:
                count += 1
        self.stdout.write(f'  Created {count} food items')

    # ── Trainers ─────────────────────────────────────────────────────────────
    def _seed_trainers(self):
        from apps.users.models import CustomUser, TrainerProfile
        trainers_data = [
            {
                'email': 'ahmed.trainer@ironforge.com',
                'first_name': 'Ahmed', 'last_name': 'Hassan',
                'specialization': 'strength', 'years_experience': 7,
                'hourly_rate': 75, 'rating': 4.9,
                'certifications': 'NSCA-CSCS, ACE Certified, Kettlebell Level 2',
                'bio': 'Elite strength coach specializing in powerlifting and athletic performance.',
            },
            {
                'email': 'sara.trainer@ironforge.com',
                'first_name': 'Sara', 'last_name': 'Mohamed',
                'specialization': 'yoga', 'years_experience': 5,
                'hourly_rate': 60, 'rating': 4.8,
                'certifications': 'RYT-500, Pre/Post-Natal Yoga, Meditation Coach',
                'bio': 'Certified yoga instructor helping clients achieve balance, flexibility and mindfulness.',
            },
            {
                'email': 'omar.trainer@ironforge.com',
                'first_name': 'Omar', 'last_name': 'Khaled',
                'specialization': 'cardio', 'years_experience': 6,
                'hourly_rate': 65, 'rating': 4.7,
                'certifications': 'ACSM-CPT, Spinning Certified, Nutrition Coach',
                'bio': 'Cardio and endurance specialist. Marathon runner and triathlete.',
            },
            {
                'email': 'nour.trainer@ironforge.com',
                'first_name': 'Nour', 'last_name': 'Ali',
                'specialization': 'nutrition', 'years_experience': 4,
                'hourly_rate': 70, 'rating': 4.8,
                'certifications': 'Registered Dietitian, Sports Nutritionist, ISSN Certified',
                'bio': 'Nutrition expert helping athletes optimize performance through food science.',
            },
        ]
        for td in trainers_data:
            spec = td.pop('specialization')
            yrs = td.pop('years_experience')
            rate = td.pop('hourly_rate')
            rating = td.pop('rating')
            certs = td.pop('certifications')

            user, created = CustomUser.objects.update_or_create(
                email=td['email'],
                defaults={
                    **td,
                    'username': td['email'],
                    'is_trainer': True,
                    'fitness_level': 'advanced',
                    'fitness_goal': 'general_fitness',
                    'password': make_password('trainer123'),
                }
            )
            TrainerProfile.objects.update_or_create(
                user=user,
                defaults={
                    'specialization': spec,
                    'years_experience': yrs,
                    'hourly_rate': rate,
                    'rating': rating,
                    'certifications': certs,
                    'is_available': True,
                    'total_sessions': random.randint(50, 300),
                }
            )
            self.stdout.write(f'  {"Created" if created else "Updated"} trainer: {user.get_full_name()}')

    # ── Members ──────────────────────────────────────────────────────────────
    def _seed_members(self):
        from apps.users.models import CustomUser
        from apps.memberships.models import MembershipPlan, UserMembership
        plans = {p.name: p for p in MembershipPlan.objects.all()}
        members_data = [
            {'email': 'ali@example.com', 'first_name': 'Ali', 'last_name': 'Mahmoud',
             'fitness_goal': 'muscle_gain', 'fitness_level': 'intermediate',
             'height_cm': 178, 'weight_kg': 75, 'plan': 'premium'},
            {'email': 'mariam@example.com', 'first_name': 'Mariam', 'last_name': 'Saad',
             'fitness_goal': 'weight_loss', 'fitness_level': 'beginner',
             'height_cm': 162, 'weight_kg': 68, 'plan': 'basic'},
            {'email': 'karim@example.com', 'first_name': 'Karim', 'last_name': 'Fathy',
             'fitness_goal': 'muscle_gain', 'fitness_level': 'advanced',
             'height_cm': 182, 'weight_kg': 88, 'plan': 'vip'},
            {'email': 'layla@example.com', 'first_name': 'Layla', 'last_name': 'Ibrahim',
             'fitness_goal': 'endurance', 'fitness_level': 'intermediate',
             'height_cm': 165, 'weight_kg': 60, 'plan': 'premium'},
            {'email': 'youssef@example.com', 'first_name': 'Youssef', 'last_name': 'Nasser',
             'fitness_goal': 'general_fitness', 'fitness_level': 'beginner',
             'height_cm': 175, 'weight_kg': 82, 'plan': 'basic'},
        ]
        for md in members_data:
            plan_name = md.pop('plan')
            user, created = CustomUser.objects.update_or_create(
                email=md['email'],
                defaults={
                    **md,
                    'username': md['email'],
                    'password': make_password('member123'),
                }
            )
            if plan_name in plans:
                UserMembership.objects.get_or_create(
                    user=user, plan=plans[plan_name],
                    defaults={
                        'start_date': timezone.now().date() - timedelta(days=random.randint(0, 20)),
                        'end_date': timezone.now().date() + timedelta(days=random.randint(10, 30)),
                        'status': 'active', 'is_active': True,
                    }
                )
            self.stdout.write(f'  {"Created" if created else "Updated"} member: {user.get_full_name()}')

    # ── Workout Programs ─────────────────────────────────────────────────────
    def _seed_workout_programs(self):
        from apps.workouts.models import WorkoutProgram, WorkoutDay, WorkoutSet, Exercise
        from apps.users.models import CustomUser

        trainer = CustomUser.objects.filter(is_trainer=True).first()
        exercises = {e.name: e for e in Exercise.objects.all()}

        programs = [
            {
                'title': 'Beginner Full Body',
                'description': 'The perfect starting point. 3 full-body sessions per week to build the foundation of strength and movement.',
                'goal': 'general_fitness', 'level': 'beginner',
                'duration_weeks': 8, 'days_per_week': 3,
                'days': [
                    {'day': 1, 'title': 'Full Body A', 'focus': 'Compound Movements',
                     'sets': [
                         ('Barbell Squat', 3, '8-10', 90),
                         ('Barbell Bench Press', 3, '8-10', 90),
                         ('Dumbbell Row', 3, '10-12', 60),
                         ('Overhead Press', 3, '10', 75),
                         ('Plank', 3, '30s', 45),
                     ]},
                    {'day': 2, 'title': 'Rest Day', 'focus': 'Recovery', 'rest': True},
                    {'day': 3, 'title': 'Full Body B', 'focus': 'Strength & Volume',
                     'sets': [
                         ('Leg Press', 4, '10-12', 75),
                         ('Push-Up', 3, '12-15', 60),
                         ('Pull-Up', 3, '6-8', 90),
                         ('Barbell Curl', 3, '12', 60),
                         ('Calf Raise', 3, '15-20', 45),
                     ]},
                    {'day': 4, 'title': 'Rest Day', 'focus': 'Recovery', 'rest': True},
                    {'day': 5, 'title': 'Full Body C', 'focus': 'Endurance',
                     'sets': [
                         ('Romanian Deadlift', 3, '10-12', 90),
                         ('Incline Dumbbell Press', 3, '12', 60),
                         ('Lateral Raise', 3, '15', 45),
                         ('Tricep Dips', 3, '10-12', 60),
                         ('Cable Crunch', 3, '15', 45),
                     ]},
                ]
            },
            {
                'title': 'Muscle Builder — PPL',
                'description': 'Classic Push/Pull/Legs split for maximum muscle hypertrophy. Train 6 days, rest 1.',
                'goal': 'muscle_gain', 'level': 'intermediate',
                'duration_weeks': 12, 'days_per_week': 6,
                'days': [
                    {'day': 1, 'title': 'Push Day', 'focus': 'Chest, Shoulders, Triceps',
                     'sets': [
                         ('Barbell Bench Press', 4, '6-8', 120),
                         ('Incline Dumbbell Press', 3, '10-12', 90),
                         ('Overhead Press', 3, '8-10', 90),
                         ('Lateral Raise', 3, '12-15', 60),
                         ('Skull Crushers', 3, '10-12', 75),
                         ('Tricep Dips', 3, '12', 60),
                     ]},
                    {'day': 2, 'title': 'Pull Day', 'focus': 'Back, Biceps',
                     'sets': [
                         ('Barbell Deadlift', 4, '5-6', 180),
                         ('Pull-Up', 4, '8-10', 90),
                         ('Dumbbell Row', 3, '10-12', 75),
                         ('Barbell Curl', 4, '10-12', 75),
                         ('Cable Crunch', 3, '15', 60),
                     ]},
                    {'day': 3, 'title': 'Leg Day', 'focus': 'Quadriceps, Hamstrings, Glutes',
                     'sets': [
                         ('Barbell Squat', 5, '6-8', 180),
                         ('Romanian Deadlift', 4, '8-10', 120),
                         ('Leg Press', 3, '12-15', 90),
                         ('Calf Raise', 4, '15-20', 60),
                         ('Plank', 3, '45s', 60),
                     ]},
                    {'day': 4, 'title': 'Push Day 2', 'focus': 'Chest, Shoulders, Triceps (Volume)',
                     'sets': [
                         ('Incline Dumbbell Press', 4, '10-12', 90),
                         ('Push-Up', 3, '15-20', 60),
                         ('Overhead Press', 4, '10', 75),
                         ('Lateral Raise', 4, '15', 45),
                         ('Skull Crushers', 4, '12', 60),
                     ]},
                    {'day': 5, 'title': 'Pull Day 2', 'focus': 'Back, Biceps (Volume)',
                     'sets': [
                         ('Pull-Up', 4, '8-10', 90),
                         ('Dumbbell Row', 4, '12', 60),
                         ('Barbell Curl', 3, '12-15', 60),
                         ('Kettlebell Swing', 3, '15', 60),
                     ]},
                    {'day': 6, 'title': 'Leg Day 2', 'focus': 'Legs (Volume)',
                     'sets': [
                         ('Leg Press', 5, '12-15', 90),
                         ('Romanian Deadlift', 3, '12', 90),
                         ('Calf Raise', 5, '20', 45),
                         ('Plank', 3, '60s', 60),
                     ]},
                    {'day': 7, 'title': 'Rest Day', 'focus': 'Full Recovery', 'rest': True},
                ]
            },
            {
                'title': 'Fat Loss Express',
                'description': 'High-intensity 4-day program combining strength and cardio to maximize fat burning.',
                'goal': 'weight_loss', 'level': 'intermediate',
                'duration_weeks': 8, 'days_per_week': 4,
                'days': [
                    {'day': 1, 'title': 'Upper Strength', 'focus': 'Chest & Back',
                     'sets': [
                         ('Push-Up', 4, '15-20', 45),
                         ('Pull-Up', 4, '8-10', 60),
                         ('Overhead Press', 3, '12', 60),
                         ('Dumbbell Row', 3, '12', 45),
                         ('Kettlebell Swing', 4, '20', 30),
                     ]},
                    {'day': 2, 'title': 'Lower Strength', 'focus': 'Legs & Core',
                     'sets': [
                         ('Barbell Squat', 4, '15', 60),
                         ('Romanian Deadlift', 3, '15', 60),
                         ('Calf Raise', 4, '20', 30),
                         ('Plank', 4, '45s', 30),
                         ('Cable Crunch', 3, '20', 30),
                     ]},
                    {'day': 3, 'title': 'Rest / Active Recovery', 'focus': 'Walk or Yoga', 'rest': True},
                    {'day': 4, 'title': 'HIIT Upper', 'focus': 'Full Upper Body Circuit',
                     'sets': [
                         ('Barbell Bench Press', 5, '10', 45),
                         ('Barbell Curl', 4, '15', 30),
                         ('Tricep Dips', 4, '15', 30),
                         ('Lateral Raise', 4, '15', 30),
                     ]},
                    {'day': 5, 'title': 'HIIT Lower', 'focus': 'Legs & Cardio Blast',
                     'sets': [
                         ('Leg Press', 5, '15', 45),
                         ('Kettlebell Swing', 5, '20', 30),
                         ('Calf Raise', 4, '25', 30),
                         ('Plank', 5, '30s', 30),
                     ]},
                ]
            },
        ]

        for prog_data in programs:
            days_data = prog_data.pop('days')
            prog, created = WorkoutProgram.objects.update_or_create(
                title=prog_data['title'],
                defaults={**prog_data, 'created_by': trainer, 'is_active': True, 'is_public': True}
            )
            # Assign all members
            from apps.users.models import CustomUser
            for m in CustomUser.objects.filter(is_trainer=False, is_staff=False):
                prog.assigned_users.add(m)

            for day_data in days_data:
                sets = day_data.pop('sets', [])
                is_rest = day_data.pop('rest', False)
                day, _ = WorkoutDay.objects.update_or_create(
                    program=prog, day_number=day_data['day'],
                    defaults={'title': day_data['title'], 'focus': day_data.get('focus', ''), 'rest_day': is_rest}
                )
                for i, (ex_name, num_sets, reps, rest) in enumerate(sets, 1):
                    if ex_name in exercises:
                        WorkoutSet.objects.update_or_create(
                            day=day, exercise=exercises[ex_name],
                            defaults={'order': i, 'sets': num_sets, 'reps': reps, 'rest_seconds': rest}
                        )
            self.stdout.write(f'  {"Created" if created else "Updated"} program: {prog.title}')

    # ── Diet Plans ───────────────────────────────────────────────────────────
    def _seed_diet_plans(self):
        from apps.diet.models import DietPlan, DietDay, Meal, MealIngredient, FoodItem
        from apps.users.models import CustomUser

        trainer = CustomUser.objects.filter(is_trainer=True).first()
        foods = {f.name: f for f in FoodItem.objects.all()}

        def make_meal(name, meal_type, ingredients):
            meal, _ = Meal.objects.get_or_create(
                name=name,
                defaults={
                    'meal_type': meal_type,
                    'prep_time_minutes': random.randint(10, 30),
                    'instructions': f'Prepare {name} as described.',
                }
            )
            for food_name, amount in ingredients:
                if food_name in foods:
                    MealIngredient.objects.get_or_create(
                        meal=meal, food_item=foods[food_name],
                        defaults={'amount_g': amount}
                    )
            return meal

        plans = [
            {
                'title': 'Muscle Gain Diet',
                'description': 'High protein, calorie surplus plan designed to maximize muscle growth while minimizing fat gain.',
                'goal': 'muscle_gain',
                'duration_weeks': 12, 'daily_calories': 3000,
                'meals': [
                    make_meal('Oatmeal Power Bowl', 'breakfast', [('Oatmeal (dry)', 80), ('Banana', 100), ('Whey Protein Powder', 30), ('Almonds', 20)]),
                    make_meal('Chicken & Rice Lunch', 'lunch', [('Chicken Breast (grilled)', 200), ('Brown Rice (cooked)', 200), ('Broccoli (steamed)', 150)]),
                    make_meal('Pre-Workout Shake', 'pre_workout', [('Whey Protein Powder', 30), ('Banana', 120), ('Skim Milk', 200)]),
                    make_meal('Salmon & Sweet Potato Dinner', 'dinner', [('Salmon (baked)', 200), ('Sweet Potato (baked)', 200), ('Spinach (raw)', 80)]),
                    make_meal('Evening Protein Snack', 'snack', [('Greek Yogurt (0% fat)', 200), ('Blueberries', 100)]),
                ]
            },
            {
                'title': 'Fat Loss Plan',
                'description': 'Calorie deficit plan with high protein to preserve muscle. Structured around satiety and steady energy.',
                'goal': 'weight_loss',
                'duration_weeks': 8, 'daily_calories': 1800,
                'meals': [
                    make_meal('Egg White Breakfast', 'breakfast', [('Eggs (whole)', 200), ('Spinach (raw)', 60), ('Bell Pepper (red)', 80)]),
                    make_meal('Tuna Salad', 'lunch', [('Tuna (canned in water)', 150), ('Mixed Salad Greens', 120), ('Cucumber', 100), ('Olive Oil', 10)]),
                    make_meal('Greek Yogurt Snack', 'snack', [('Greek Yogurt (0% fat)', 200), ('Apple', 150)]),
                    make_meal('Grilled Chicken Bowl', 'dinner', [('Chicken Breast (grilled)', 180), ('Quinoa (cooked)', 150), ('Broccoli (steamed)', 200)]),
                ]
            },
            {
                'title': 'Maintenance & Performance',
                'description': 'Balanced macronutrient plan to maintain weight and support peak athletic performance.',
                'goal': 'maintenance',
                'duration_weeks': 12, 'daily_calories': 2400,
                'meals': [
                    make_meal('Performance Breakfast', 'breakfast', [('Eggs (whole)', 150), ('Whole Wheat Bread', 80), ('Avocado', 60)]),
                    make_meal('Balanced Lunch', 'lunch', [('Chicken Breast (grilled)', 150), ('White Rice (cooked)', 150), ('Mixed Salad Greens', 100)]),
                    make_meal('Afternoon Snack', 'snack', [('Peanut Butter (natural)', 30), ('Apple', 150)]),
                    make_meal('Recovery Dinner', 'dinner', [('Salmon (baked)', 150), ('Quinoa (cooked)', 150), ('Broccoli (steamed)', 150)]),
                    make_meal('Post-Workout Recovery', 'post_workout', [('Whey Protein Powder', 30), ('Banana', 100), ('Skim Milk', 300)]),
                ]
            },
        ]

        for plan_data in plans:
            meals = plan_data.pop('meals')
            plan, created = DietPlan.objects.update_or_create(
                title=plan_data['title'],
                defaults={**plan_data, 'created_by': trainer, 'is_active': True, 'is_public': True}
            )
            # Assign to all members
            from apps.users.models import CustomUser
            for m in CustomUser.objects.filter(is_trainer=False, is_staff=False):
                plan.assigned_users.add(m)

            # Create 7-day plan
            for day_num in range(1, 8):
                day, _ = DietDay.objects.get_or_create(
                    plan=plan, day_number=day_num,
                    defaults={'title': f'Day {day_num}'}
                )
                for meal in meals:
                    day.meals.add(meal)

            self.stdout.write(f'  {"Created" if created else "Updated"} diet plan: {plan.title}')

    # ── Training Sessions ────────────────────────────────────────────────────
    def _seed_sessions(self):
        from apps.bookings.models import TrainingSession
        from apps.users.models import CustomUser

        trainers = list(CustomUser.objects.filter(is_trainer=True))
        if not trainers:
            return

        today = timezone.now().date()
        sessions = [
            # Personal sessions
            {'title': 'Strength Fundamentals', 'type': 'personal', 'days': 1, 'time': ('07:00', '08:00'), 'max': 1, 'price': 0},
            {'title': 'Power & Conditioning', 'type': 'personal', 'days': 2, 'time': ('09:00', '10:00'), 'max': 1, 'price': 0},
            {'title': 'Fat Burn Circuit', 'type': 'personal', 'days': 3, 'time': ('18:00', '19:00'), 'max': 1, 'price': 0},
            {'title': 'Mobility & Recovery', 'type': 'personal', 'days': 4, 'time': ('08:00', '09:00'), 'max': 1, 'price': 0},
            {'title': 'Advanced Powerlifting', 'type': 'personal', 'days': 5, 'time': ('06:30', '07:30'), 'max': 1, 'price': 0},
            # Group sessions
            {'title': 'Morning HIIT Blast', 'type': 'group', 'days': 1, 'time': ('06:00', '07:00'), 'max': 12, 'price': 0},
            {'title': 'Yoga Flow — All Levels', 'type': 'group', 'days': 2, 'time': ('10:00', '11:00'), 'max': 15, 'price': 0},
            {'title': 'Core & Abs Blitz', 'type': 'group', 'days': 2, 'time': ('19:00', '19:45'), 'max': 20, 'price': 0},
            {'title': 'Spin Class — Intermediate', 'type': 'group', 'days': 3, 'time': ('07:00', '08:00'), 'max': 10, 'price': 0},
            {'title': 'Full Body Strength', 'type': 'group', 'days': 3, 'time': ('18:30', '19:30'), 'max': 15, 'price': 0},
            {'title': 'Pilates & Flexibility', 'type': 'group', 'days': 4, 'time': ('11:00', '12:00'), 'max': 12, 'price': 0},
            {'title': 'Boxing Fundamentals', 'type': 'group', 'days': 5, 'time': ('18:00', '19:00'), 'max': 10, 'price': 0},
            {'title': 'Weekend Warrior HIIT', 'type': 'group', 'days': 6, 'time': ('09:00', '10:00'), 'max': 20, 'price': 0},
            # Online
            {'title': 'Online Nutrition Coaching', 'type': 'online', 'days': 3, 'time': ('16:00', '17:00'), 'max': 5, 'price': 0},
            {'title': 'Virtual Form Check', 'type': 'online', 'days': 6, 'time': ('11:00', '11:30'), 'max': 3, 'price': 0},
        ]

        count = 0
        for i, s in enumerate(sessions):
            trainer = trainers[i % len(trainers)]
            session_date = today + timedelta(days=s['days'])
            _, created = TrainingSession.objects.get_or_create(
                trainer=trainer,
                title=s['title'],
                date=session_date,
                defaults={
                    'session_type': s['type'],
                    'start_time': s['time'][0],
                    'end_time': s['time'][1],
                    'max_participants': s['max'],
                    'price': s['price'],
                    'location': random.choice(['Main Floor', 'Studio A', 'Studio B', 'Cardio Zone', 'Online']),
                    'status': 'open',
                }
            )
            if created:
                count += 1
        self.stdout.write(f'  Created {count} training sessions')

    # ── Bookings ─────────────────────────────────────────────────────────────
    def _seed_bookings(self):
        from apps.bookings.models import TrainingSession, Booking
        from apps.users.models import CustomUser
        from apps.payments.models import Payment
        from apps.memberships.models import MembershipPlan, UserMembership

        members = list(CustomUser.objects.filter(is_trainer=False, is_staff=False))
        sessions = list(TrainingSession.objects.filter(status='open'))
        if not members or not sessions:
            return

        count = 0
        for member in members:
            # Book 2-3 sessions per member
            for session in random.sample(sessions, min(3, len(sessions))):
                if session.spots_remaining > 0:
                    _, created = Booking.objects.get_or_create(
                        user=member, session=session,
                        defaults={'status': 'confirmed'}
                    )
                    if created:
                        count += 1

        # Add some past completed bookings + payments
        plan = MembershipPlan.objects.filter(name='premium').first()
        for member in members:
            Payment.objects.get_or_create(
                user=member,
                stripe_payment_intent_id=f'pi_demo_{member.id}',
                defaults={
                    'amount': random.choice([29, 59, 99]),
                    'currency': 'USD',
                    'status': 'succeeded',
                    'payment_type': 'membership',
                    'description': f'Membership subscription',
                }
            )
        self.stdout.write(f'  Created {count} bookings')

    # ── Admin ─────────────────────────────────────────────────────────────────
    def _seed_admin(self):
        from apps.users.models import CustomUser
        admin, created = CustomUser.objects.update_or_create(
            email='admin@ironforge.com',
            defaults={
                'username': 'admin@ironforge.com',
                'first_name': 'Admin',
                'last_name': 'IronForge',
                'is_staff': True,
                'is_superuser': True,
                'password': make_password('admin123'),
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('  Created admin: admin@ironforge.com / admin123'))
        else:
            self.stdout.write('  Admin already exists')

    def _print_summary(self):
        from apps.users.models import CustomUser
        from apps.memberships.models import MembershipPlan, UserMembership
        from apps.workouts.models import WorkoutProgram, Exercise
        from apps.diet.models import DietPlan, FoodItem
        from apps.bookings.models import TrainingSession, Booking

        self.stdout.write(self.style.MIGRATE_HEADING('\n📊 Database Summary:'))
        self.stdout.write(f'  👥 Users: {CustomUser.objects.count()} ({CustomUser.objects.filter(is_trainer=True).count()} trainers)')
        self.stdout.write(f'  💳 Plans: {MembershipPlan.objects.count()}')
        self.stdout.write(f'  🏅 Active memberships: {UserMembership.objects.filter(is_active=True).count()}')
        self.stdout.write(f'  🏋️  Programs: {WorkoutProgram.objects.count()} | Exercises: {Exercise.objects.count()}')
        self.stdout.write(f'  🥗 Diet plans: {DietPlan.objects.count()} | Foods: {FoodItem.objects.count()}')
        self.stdout.write(f'  📅 Sessions: {TrainingSession.objects.count()} | Bookings: {Booking.objects.count()}')
        self.stdout.write(self.style.MIGRATE_HEADING('\n🔑 Login Credentials:'))
        self.stdout.write('  Admin:   admin@ironforge.com  /  admin123')
        self.stdout.write('  Trainer: ahmed.trainer@ironforge.com  /  trainer123')
        self.stdout.write('  Member:  ali@example.com  /  member123')
