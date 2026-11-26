import os
import random
import django

#TODO: Reviews, messages

# Ensure Django settings are properly loaded
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

# Import additional modules (Django has to be loaded before importing project models)
from accounts.models.profile import *
from messaging.models.chat import *
from services.models.listing import *
from faker import Faker
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from services.engagements import complete_engagement, decide_request, start_request_chat, submit_engagement_review
from services.models.engagement import ListingRequest
from messaging.services import send_message

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
            test_users.append(User(
                username = email,
                email = email,
                password = HASHED_PASSWORD,
                first_name = fake.first_name(),
                last_name = fake.last_name()
            ))

        User.objects.bulk_create(test_users)

        Profile.objects.bulk_create([
            Profile(
                user = user,
                skills = random.choice(Profile.SKILL_CHOICES),
                interests = fake.words(5, unique=True),
                bio = fake.sentences(nb=5)[:500]
            )
            for user in test_users
        ])
        print(f'{count} sample users created successfully!')
        return test_users
    
    except Exception as e:
        print(f'Error creating users: {e}')

def generate_listings(count, users, real_author=None):
    """
    Generates and inserts *count* number of service listings into database.
    Authors are picked at random from existing users.
    *NOTE: THERE MUST BE USERS AVAILABLE IN DB FOR THIS FUNCTION TO WORK*
    """
    print('Generating Test Service listings...')
    try:
        if not users:
            print('No users found. Run generate_user_profiles first.')
            return

        test_listings = [
            Listing(
                author = (real_author if i % 2 == 0 and real_author is not None else random.choice(users)),
                service_type = random.choice(Listing.ServiceType.values),
                title = fake.sentence(nb_words=10)[:100],
                description = fake.paragraph()[:2000],
                category = random.choice(service_types)[0],
                date = fake.date_between(start_date='today', end_date='+60d')
            )
            for i in range(count)
        ]

        print(f'{count} sample listings created successfully!')
        return Listing.objects.bulk_create(test_listings)

    except Exception as e:
        print(f'Error creating listings: {e}')


def generate_engagments_and_reviews(listings, users, real_author=None, *, complete):
  
    """
    Generates sample user reviews between existing users.
    A user cannot review themselves, and each reviewer/reviewed-user
    pair can only exist once.
    """

    print('Generating Test User Reviews...')
    users = list(User.objects.all())
    try:
        if len(users) < 2:
            print('Not enough users found. At least 2 users are required.')
            return

        for listing in listings:
            requester = random.choice([user for user in users if user.pk != listing.author_id])
            item = ListingRequest.objects.create(listing=listing, requester=requester)
            item = start_request_chat(listing.pk, item.pk, listing.author)
            if real_author is not None and real_author.pk in (listing.author_id,requester.pk):
                for i in range(4):
                    send_message(item.chat, requester, fake.sentence(nb_words=10)[:100])
                    send_message(item.chat, listing.author, fake.sentence(nb_words=10)[:100])

            decide_request(listing.pk, item.pk, requester, agree=True)
            if complete:
                decide_request(listing.pk, item.pk, listing.author, agree=True)
                complete_engagement(listing.pk, requester)

                for reviewer in (listing.author, requester):
                    submit_engagement_review(
                        listing.pk,
                        reviewer,
                        rating=random.randint(4, 5),
                        comment=random.choice([
                            "Really helpful and easy to work with.",
                            "Great communication and very reliable.",
                            "Had a great experience working with them.",
                            "Very friendly and knowledgeable.",
                            "Would definitely work with them again.",
                            "Super helpful and responded quickly.",
                            "Made the whole process really easy.",
                        ]),
                    )

            UnreadChat.objects.filter(chat_id=item.chat_id).delete()

        print('sample user reviews created successfully!')

    except Exception as e:
        print(f'Error creating user reviews: {e}')
       


if __name__ == '__main__':
    username = input("Enter username for half of the entries to be tied to your account (Enter for purely test accounts): ")
    real_author = None
    if username:
        try:
            real_author = User.objects.get(username=username)
        except User.DoesNotExist:
            raise SystemExit("No such account.")
    num_records = int(input('Enter number of entries to generate: '))
    users = generate_user_profiles(num_records)
    listings = generate_listings(num_records, users, real_author)
    completed = num_records // 2
    pending = completed + min(2, completed)
    generate_engagments_and_reviews(listings[:completed], users, real_author, complete=True)
    generate_engagments_and_reviews(listings[completed:pending], users, real_author, complete=False)
