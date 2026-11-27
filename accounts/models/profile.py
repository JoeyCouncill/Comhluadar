from django.conf import settings
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
        ("Tutoring", "Tutoring"),
        ("Technology", "Technology"),
        ("Automotive", "Automotive"),
        ("Art-design", "Art & Design"),
        ("Photography", "Photography"),
        ("Repairs", "Repairs"),
        ("Other", "Other"),
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


class UserReport(models.Model):
    class Category(models.TextChoices):
        HARASSMENT = "harassment", "Harassment or Bullying"
        INAPPROPRIATE = "inappropriate", "Inappropriate Behavior"
        SPAM = "spam", "Spam or Scams"
        FRAUD = "fraud", "Fraud or Misrepresentation"
        THREATS = "threats", "Threats or Safety Concerns"
        DISCRIMINATION = "discrimination", "Discrimination or Hate Speech"
        OTHER = "other", "Other"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending Review"
        REVIEWED = "reviewed", "Reviewed"
        RESOLVED = "resolved", "Resolved"

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reports_submitted",
    )
    reported_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reports_received",
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
    )
    description = models.TextField(max_length=2000)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(
                    reporter=models.F("reported_user")
                ),
                name="prevent_self_report",
            ),
        ]

    def __str__(self):
        return f"Report #{self.pk} - {self.get_category_display()}"
