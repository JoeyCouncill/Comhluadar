from django.db import models

# Table  ServiceCategoryLookup
class ServiceCategoryLookup(models.Model):
    service_category_id = models.AutoField(primary_key=True)
    service_category_name = models.CharField(max_length=200)
    service_category_status = models.CharField(max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self

# Table  ServiceRatingLookup
class ServiceRatingLookup(models.Model):
    rating_id = models.AutoField(primary_key=True)
    rating_description = models.CharField(max_length=200)
    rating_status = models.CharField(max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self

# Table  UserServices
class UserServices(models.Model):
    service_id = models.AutoField(primary_key=True)
    service_user_id = models.IntegerField()
    service_category_id = models.IntegerField()
    service_description = models.CharField(max_length=255)
    service_status = models.CharField(max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self

# Table  UserRequests
class UserRequests(models.Model):
    request_id = models.AutoField(primary_key=True)
    requested_user_id = models.IntegerField()
    request_category_id = models.IntegerField()
    request_description = models.CharField(max_length=255)
    created_date = models.DateTimeField(auto_now_add=True)
    request_feedback = models.CharField(max_length=255)
    request_status = models.CharField(max_length=50)
    created_date = models.DateTimeField()
    completed_user_id = models.IntegerField()
    user_rating_id = models.IntegerField()

    def __str__(self):
        return self

# Table  UserMessaging
class UserMessaging(models.Model):
    messaging_id = models.AutoField(primary_key=True)
    request_id = models.IntegerField()
    request_user_id = models.IntegerField()
    service_user_id = models.IntegerField()
    message_user_id = models.IntegerField()
    message = models.CharField(max_length=255)
    created_date = models.DateTimeField(auto_now_add=True)
    message_status = models.CharField(max_length=50)
 
    def __str__(self):
        return self

# Table UserRating
class UserRating(models.Model):
    user_rating_id = models.AutoField(primary_key=True)
    request_id = models.IntegerField()
    request_user_id = models.IntegerField()
    service_user_id = models.IntegerField()
    rating_user_id = models.IntegerField()
    rating_id = models.IntegerField()
    submit_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self

# Table BlockedUsers
class BlockedUsers(models.Model):
    blocked_id = models.AutoField(primary_key=True)
    blocked_by_user_id = models.IntegerField()
    blocked_user_id = models.IntegerField()
    blocked_date = models.DateTimeField()
    unblocked_date = models.DateTimeField() 
    current_blocked_user_status = models.CharField(max_length=50)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self