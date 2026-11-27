from django.contrib import admin

from .models import UserReport


@admin.register(UserReport)
class UserReportAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "reporter",
        "reported_user",
        "category",
        "status",
        "created_at",
    )

    list_filter = ("category", "status", "created_at")
    search_fields = (
        "reporter__username",
        "reported_user__username",
        "description",
    )

    readonly_fields = (
        "reporter",
        "reported_user",
        "category",
        "description",
        "created_at",
    )
