import os
import random
import django

#TODO: Reviews, messages

# Ensure Django settings are properly loaded
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Comhluadar.settings')
django.setup()

# Import additional modules (Django has to be loaded before importing project models)
from accounts.models import *
from messaging.models import *
from services.models import *
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
        test_users = []
        for i in range(count):
            email = fake.unique.email()
            test_users.append(
                User(
                username = email,
                email = email,
                password = HASHED_PASSWORD,
                first_name = fake.first_name(),
                last_name = fake.last_name()
            )
        )

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

def generate_listings(count=10):
    """
    Generates and inserts *count* number of service listings into database.
    Authors are picked at random from existing users.
    *NOTE: THERE MUST BE USERS AVAILABLE IN DB FOR THIS FUNCTION TO WORK*
    """
    print('Generating Test Service listings...')

    try:
        users = list(User.objects.all())
        if not users:
            print('No users found. Run generate_user_profiles first.')
            return

        test_services = [Listing(
            author = random.choice(users),
            service_type = random.choice(Listing.ServiceType.values),
            title = fake.sentence(nb_words=10),
            description = fake.paragraph(),
            category = random.choice(service_types)[0],
            date = fake.date_between(start_date='today', end_date='+60d')
        )
        for i in range(count)
        ]

        Listing.objects.bulk_create(test_services)

        print(f'{count} sample listings created successfully!')

    except Exception as e:
        print(f'Error creating listings: {e}')

if __name__ == '__main__':
    num_records = int(input('Enter number of entries to generate: '))
    generate_user_profiles(num_records)
    generate_listings(num_records)