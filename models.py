from django.db import models

class User(models.Model):
    id = models.IntegerField(primary_key=True)
    password = models.CharField(max_length=45, null=True, blank=True)
    last_login = models.DateTimeField(
        db_column="lat_login", null=True, blank=True
    )
    is_superuser = models.BooleanField(null=True, blank=True)
    username = models.CharField(
        max_length=45, unique=True, null=True, blank=True
    )
    first_name = models.CharField(max_length=45, null=True, blank=True)
    last_name = models.CharField(max_length=45, null=True, blank=True)
    email = models.EmailField(max_length=200, null=True, blank=True)
    is_staff = models.BooleanField(null=True, blank=True)
    is_active = models.BooleanField(null=True, blank=True)
    date_joined = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "comhluadar_user"

    def __str__(self):
        return self.username or f"User {self.id}"

class ServiceCategory(models.Model):
    service_category_id = models.AutoField(primary_key=True)
    service_category_name = models.CharField(max_length=200)
    service_category_status = models.CharField(
        max_length=45, null=True, blank=True
    )

    class Meta:
        db_table = "service_category_lookup"

    def __str__(self):
        return self.service_category_name

class UserService(models.Model):
    service_id = models.AutoField(primary_key=True)
    service_user = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        db_column="service_user_id",
        related_name="services",
    )
    service_category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.DO_NOTHING,
        db_column="service_category_id",
        related_name="services",
        null=True,
        blank=True,
    )
    service_description = models.CharField(max_length=4000)
    created_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "user_services"

    def __str__(self):
        return f"Service {self.service_id}"

class UserRequest(models.Model):
    request_id = models.AutoField(primary_key=True)
    request_user = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        db_column="request_user_id",
        related_name="requests",
    )
    request_category = models.ForeignKey(
        ServiceCategory,
        on_delete=models.DO_NOTHING,
        db_column="request_category_id",
        related_name="requests",
        null=True,
        blank=True,
    )
    request_description = models.CharField(max_length=4000)
    created_date = models.DateTimeField()
    service_feedback = models.CharField(
        max_length=4000, null=True, blank=True
    )
    request_status = models.CharField(
        max_length=45, null=True, blank=True
    )
    completed_date = models.DateTimeField(null=True, blank=True)
    completed_user_id = models.IntegerField(null=True, blank=True)
    rating_id = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "user_requests"

    def __str__(self):
        return f"Request {self.request_id}"

class UserMessage(models.Model):
    messaging_id = models.AutoField(primary_key=True)
    request = models.ForeignKey(
        UserRequest,
        on_delete=models.DO_NOTHING,
        db_column="request_id",
        related_name="messages",
    )
    request_user_id = models.IntegerField()
    service_user_id = models.IntegerField(null=True, blank=True)
    message_user_id = models.IntegerField()
    message = models.CharField(max_length=4000, null=True, blank=True)
    created_date = models.DateTimeField()
    message_status = models.CharField(
        max_length=45, null=True, blank=True
    )

    class Meta:
        db_table = "user_messaging"

    def __str__(self):
        return f"Message {self.messaging_id}"

class RatingCategory(models.Model):
    rating_id = models.AutoField(primary_key=True)
    rating_description = models.CharField(max_length=200)
    rating_status = models.CharField(
        max_length=45, null=True, blank=True
    )

    class Meta:
        db_table = "user_rating_lookup"

    def __str__(self):
        return self.rating_description

class UserRating(models.Model):
    user_rating_id = models.AutoField(primary_key=True)
    request = models.ForeignKey(
        UserRequest,
        on_delete=models.DO_NOTHING,
        db_column="request_id",
        related_name="ratings",
    )
    request_user_id = models.IntegerField(null=True, blank=True)
    service_user_id = models.IntegerField(null=True, blank=True)
    rating_user_id = models.IntegerField(null=True, blank=True)
    rating = models.ForeignKey(
        RatingCategory,
        on_delete=models.DO_NOTHING,
        db_column="rating_id",
        related_name="user_ratings",
        null=True,
        blank=True,
    )
    submit_date = models.DateTimeField()

    class Meta:
        db_table = "user_rating"

    def __str__(self):
        return f"Rating {self.user_rating_id}"

class BlockedUser(models.Model):
    pk = models.CompositePrimaryKey(
        "blocked_by_user", "blocked_user"
    )
    blocked_by_user = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        db_column="blocked_by_user_id",
        related_name="blocked_users",
    )
    blocked_user = models.ForeignKey(
        User,
        on_delete=models.DO_NOTHING,
        db_column="blocked_user_id",
        related_name="blocked_by",
    )
    blocked_date = models.DateTimeField(null=True, blank=True)
    unblocked_date = models.DateTimeField(null=True, blank=True)
    current_user_status = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = "blocked_users"

    def __str__(self):
        return (
            f"{self.blocked_by_user_id} blocked "
            f"{self.blocked_user_id}"
        )
