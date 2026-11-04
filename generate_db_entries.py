import os
import random
import django

#TODO: Reviews, messages

# Ensure Django settings are properly loaded
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Comhluadar.settings')
django.setup()

# Import additional modules (Django has to be loaded before importing project models)
from accounts_app.models import *
from message_app.models import *
from service_app.models import *
from faker import Faker
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

fake = Faker()
User = get_user_model()

TEST_PASSWORD = 'This!sAT357P455w0rd'
HASHED_PASSWORD = make_password(TEST_PASSWORD)

def generate_user_profiles(count=10):
    """
    Generates and inserts *count* number of users into database. All generated accounts share 'TEST_PASSWORD'
    """
    print('Generating Test User Profiles...')

    try:
        test_users = [User(
            username = fake.unique.user_name(),
            email = fake.unique.email(),
            password = HASHED_PASSWORD,
            first_name = fake.first_name(),
            last_name = fake.last_name()
        )
        for i in range(count)
        ]

        User.objects.bulk_create(test_users)

        test_profiles = [Profile(
            user = user,
            skills = random.choice(Profile.SKILL_CHOICES),
            interests = fake.words(5, unique=True),
            bio = fake.sentences(nb=5)[:500]
        )
        for user in test_users
        ]

        Profile.objects.bulk_create(test_profiles)

        print(f'{count} sample users created successfully!')

    except Exception as e:
        print(f'Error creating users: {e}')

def generate_posts(count=10):
    """
    Generates and inserts *count* number of service posts into database.
    Authors are picked at random from existing users.
    *NOTE: THERE MUST BE USERS AVAILABLE IN DB FOR THIS FUNCTION TO WORK*
    """
    print('Generating Test Service Posts...')

    try:
        users = list(User.objects.all())
        if not users:
            print('No users found. Run generate_user_profiles first.')
            return

        test_services = [Service(
            author = random.choice(users),
            listing_type = random.choice(Service.ListingType.values),
            title = fake.sentence(nb_words=10),
            description = fake.paragraph(),
            category = random.choice(service_types)[0],
            date = fake.date_between(start_date='today', end_date='+60d')
        )
        for i in range(count)
        ]

        Service.objects.bulk_create(test_services)

        print(f'{count} sample posts created successfully!')

    except Exception as e:
        print(f'Error creating services: {e}')

if __name__ == '__main__':
    num_records = int(input('Enter number of entries to generate: '))
    generate_user_profiles(num_records)
    generate_posts(num_records)