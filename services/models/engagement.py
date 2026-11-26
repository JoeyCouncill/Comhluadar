from django.conf import settings
from django.db import models


class ListingRequest(models.Model):
    listing = models.ForeignKey(
        "services.Listing",
        on_delete=models.CASCADE,
        related_name="engagement_requests",
    )
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="listing_requests",
    )
    chat = models.OneToOneField(
        "messaging.Chat",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
    )
    author_agreed_at = models.DateTimeField(null=True, blank=True)
    requester_agreed_at = models.DateTimeField(null=True, blank=True)
    declined_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    class DeclinedBy(models.TextChoices):
        AUTHOR = "author", "Listing author"
        REQUESTER = "requester", "Requester"

    declined_by_role = models.CharField(max_length=9, choices=DeclinedBy.choices, blank=True, default="")
    decision_round = models.PositiveIntegerField(default=1)


    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["listing", "requester"],
                condition=models.Q(declined_at__isnull=True),
                name="one_nondeclined_request_per_listing_user",
            ),
        ]

    @property
    def is_open(self):
        return self.declined_at is None and not hasattr(self.listing, "engagement")

    @property
    def can_decide(self):
        return self.chat_id is not None and self.is_open

    @property
    def status_label(self):
        if self.declined_at:
            return "Declined"

        engagement = getattr(self.listing, "engagement", None)
        if engagement:
            if engagement.request_id == self.pk:
                if engagement.completed_at is not None:
                    return "Engagement completed"
                return "Engagement confirmed"
            return "Listing no longer available"

        return "Discussing" if self.chat_id else "Waiting for the author to start a chat"


class Engagement(models.Model):
    listing = models.OneToOneField(
        "services.Listing",
        on_delete=models.CASCADE,
        related_name="engagement",
    )
    request = models.OneToOneField(
        ListingRequest,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    confirmed_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)