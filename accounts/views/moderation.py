from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from accounts.models import UserBlock, UserReport
from accounts.forms import UserReportForm


User = get_user_model()


@login_required
@require_POST
def block_user(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)

    if target_user.pk == request.user.pk:
        messages.error(request, "You cannot block yourself.")
        return redirect("account_summary")

    block, created = UserBlock.objects.get_or_create(
        blocker=request.user,
        blocked=target_user,
    )

    if created:
        messages.success(request, "User blocked successfully.")
    else:
        messages.info(request, "This user is already blocked.")

    return redirect("user_profile", user_id=target_user.pk)


@login_required
@require_POST
def unblock_user(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)

    deleted_count, _ = UserBlock.objects.filter(
        blocker=request.user,
        blocked=target_user,
    ).delete()

    if deleted_count:
        messages.success(request, "User unblocked successfully.")
    else:
        messages.info(request, "You have not blocked this user.")

    return redirect("user_profile", user_id=target_user.pk)


@login_required
def report_user(request, user_id):
    target_user = get_object_or_404(User, pk=user_id)

    if target_user.pk == request.user.pk:
        messages.error(request, "You cannot report yourself.")
        return redirect("account_summary")

    if request.method == "POST":
        form = UserReportForm(request.POST)

        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.reported_user = target_user
            report.save()

            messages.success(
                request,
                "Your report has been submitted for review."
            )
            return redirect("user_profile", user_id=target_user.pk)
    else:
        form = UserReportForm()

    return render(
        request,
        "report_user.html",
        {
            "form": form,
            "target_user": target_user,
        },
    )
