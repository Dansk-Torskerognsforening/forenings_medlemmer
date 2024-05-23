from typing import Any
from django.contrib import admin
from django.db.models import Q
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

# from members.models import EmailItem

from members.models import (
    EmailItem,
    Activity,
    Department,
)


class activityFilter(admin.SimpleListFilter):
    title = _("Aktivitet")
    parameter_name = "activity"

    def lookups(self, request: Any, model_admin: Any) -> list[tuple[Any, str]]:
        year = ""
        month = ""
        day = ""
        if "created_dtm__year" in request.GET:
            year = request.GET["created_dtm__year"]
            queryset = EmailItem.objects.filter(created_dtm__year=year)
            if "created_dtm__month" in request.GET:
                month = request.GET["created_dtm__month"]
                queryset = queryset.filter(created_dtm__month=month)
                if "created_dtm__day" in request.GET:
                    day = request.GET["created_dtm__day"]
                    queryset = queryset.filter(created_dtm__day=day)
            activities = (
                queryset.filter(activity__isnull=False)
                .values_list("activity", flat=True)
                .distinct()
            )
        else:
            activities = (
                EmailItem.objects.filter(activity__isnull=False)
                .values_list("activity", flat=True)
                .distinct()
            )
        filtervalue = ""
        if len(month) == 1:
            month = f"0{month}"
        if len(day) == 1:
            day = f"0{day}"

        if year != "":
            filtervalue = year

        if month != "":
            filtervalue += f"-{month}"
        if day != "":
            filtervalue += f"-{day}"
        if filtervalue != "":
            self.title = f"Aktivitet (mail {filtervalue})"

        activityList = [("none", "(Ingen aktivitet)")]
        for activity in Activity.objects.filter(id__in=activities).order_by("name"):
            activityList.append((str(activity.id), str(activity.name)))
        return activityList
        # return [
        # (str(activity.id), str(activity.name))

    #            for activity in Activity.objects.filter(id__in=activities).order_by("name")
    #       ]

    def queryset(self, request, queryset):
        if self.value() == "none":
            return queryset.filter(activity__isnull=True).distinct()
        if self.value():
            return queryset.filter(activity=self.value()).order_by("activity__name")
        return queryset.order_by("activity__name")


class departmentFilter(admin.SimpleListFilter):
    title = _("Afdeling")
    parameter_name = "department__calculated"

    def lookups(self, request: Any, model_admin: Any) -> list[tuple[Any, str]]:
        year = ""
        month = ""
        day = ""
        if "created_dtm__year" in request.GET:
            year = request.GET["created_dtm__year"]
            queryset = EmailItem.objects.filter(created_dtm__year=year)
            if "created_dtm__month" in request.GET:
                month = request.GET["created_dtm__month"]
                queryset = queryset.filter(created_dtm__month=month)
                if "created_dtm__day" in request.GET:
                    day = request.GET["created_dtm__day"]
                    queryset = queryset.filter(created_dtm__day=day)
            departments = (
                queryset.filter(department__isnull=False)
                .values_list("department__id", flat=True)
                .order_by("department__name")
                .distinct()
            )

            departments = departments.union(
                queryset.filter(activity__department__isnull=False)
                .values_list("activity__department__id", flat=True)
                .order_by("activity__department__name")
                .distinct()
            )

        else:
            departments = EmailItem.objects.values_list(
                "department", flat=True
            ).distinct()
            departments = departments.union(
                EmailItem.objects.values_list(
                    "activity__department", flat=True
                ).distinct()
            )
        filtervalue = ""
        if len(month) == 1:
            month = f"0{month}"
        if len(day) == 1:
            day = f"0{day}"

        if year != "":
            filtervalue = year

        if month != "":
            filtervalue += f"-{month}"
        if day != "":
            filtervalue += f"-{day}"
        if filtervalue != "":
            self.title = f"Afdeling (mail {filtervalue})"

        return [
            (str(department.id), str(department.name))
            for department in Department.objects.filter(id__in=departments).order_by(
                "name"
            )
        ]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(department=self.value()).order_by("department")
        return queryset.order_by("department")


class EmailItemAdmin(admin.ModelAdmin):
    list_display = [
        "created_dtm",
        "receiver",
        "departmentName",
        "activityName",
        "subject",
    ]
    list_filter = [
        departmentFilter,
        activityFilter,
    ]

    date_hierarchy = "created_dtm"
    search_fields = ("person__name", "family__email", "activity__name", "subject")
    search_help_text = mark_safe(
        "Du kan søge på personnavn, familie-email, afdelingsnavn, aktivitetsnavn eller email emne.<br>Vandret dato-filter er for hvornår emailen er oprettet"
    )
    readonly_fields = ("created_dtm", "send_error", "sent_dtm")

    fieldsets = [
        (
            "Modtager information",
            {
                "description": "Information om modtager (navn, familie, email)",
                "fields": (
                    "person",
                    "receiver",
                    "family",
                ),
            },
        ),
        (
            "Email information",
            {
                "description": "Indhold i email",
                "fields": (
                    "created_dtm",
                    "subject",
                    "body_text",
                    "body_html",
                ),
            },
        ),
        (
            "Yderlige data",
            {
                "description": "Diverse information om denne email",
                "fields": (
                    "template",
                    "bounce_token",
                    "activity",
                    "department",
                    "sent_dtm",
                    "send_error",
                ),
                "classes": ("collapse",),
            },
        ),
    ]
