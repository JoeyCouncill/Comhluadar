from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.templatetags.static import static


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    @property
    def display_name(self):
        return self.user.email.partition("@")[0]

    @property
    def profile_picture_url(self):
        if self.profile_picture:
            return self.profile_picture.url
        return static("images/default_pfp.svg.webp")
    
    ##djangos built in AUTH_USER_MODEL already holds email, password, username, first name, and last name
    ##the profile model is for adding fields we want on the profile page/other than the above mentioned fields (: 

    SKILL_CHOICES = [
        ("tutoring", "Tutoring"),
        ("technology", "Technology"),
        ("automotive", "Automotive"),
        ("art-design", "Art & Design"),
        ("photography", "Photography"),
        ("repairs", "Repairs"),
        ("other", "Other"),
    ]

    skills = models.CharField(max_length=20, choices=SKILL_CHOICES, blank=True)
    other_skill = models.CharField(max_length=100, blank=True)
    interests = models.CharField(max_length=255, blank=True)
    bio = models.TextField(max_length=500, blank=True)

    profile_picture = models.ImageField(
        upload_to="profiles/pfp/",
        blank=True,
    )
    cover_photo = models.ImageField(
        upload_to="profiles/covers/",
        blank=True,
    )

    def __str__(self):
        return f"{self.user.get_username()}'s profile"

class UserReview(models.Model):
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews_written",
    )
    reviewed_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews_received",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["reviewer", "reviewed_user"],
                name="unique_user_review",
            ),
            models.CheckConstraint(
                condition=~models.Q(reviewer=models.F("reviewed_user")),
                name="prevent_self_review",
            ),
            models.CheckConstraint(
                condition=models.Q(rating__gte=1, rating__lte=5),
                name="user_rating_between_1_and_5",
            ),
        ]


class UserBlock(models.Model):
    blocker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blocks_created",
    )
    blocked = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blocks_received",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["blocker", "blocked"],
                name="unique_user_block",
            ),
            models.CheckConstraint(
                condition=~models.Q(blocker=models.F("blocked")),
                name="prevent_self_block",
            ),
        ]