import asyncio

from django.conf import settings
from django.contrib import admin, messages
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path
from temporalio.client import Client

from health_activities.models import CaloriesPerMonth, HealthActivity
from health_activities.workflows import ProcessMonthlyHealthActivitiesWorkflow


@admin.register(HealthActivity)
class HealthActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'duration', 'calories_burned', 'user')
    search_fields = ('name',)
    list_filter = ('user',)


@admin.register(CaloriesPerMonth)
class CaloriesPerMonthAdmin(admin.ModelAdmin):
    list_display = ('user', 'month', 'year', 'calories')
    search_fields = ('user__username',)
    list_filter = ('user',)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'trigger-processing/',
                self.admin_site.admin_view(self.trigger_processing_view),
                name='health_activities_trigger_processing',
            ),
        ]
        return custom_urls + urls

    def trigger_processing_view(self, request):
        if request.method == 'POST':
            async def run_workflow():
                client = await Client.connect(settings.TEMPORAL_SERVER_URL)
                await client.start_workflow(
                    ProcessMonthlyHealthActivitiesWorkflow.run,
                    id="manual-monthly-health-activities",
                    task_queue="health-activities"
                )

            try:
                asyncio.run(run_workflow())
                self.message_user(
                    request,
                    "Monthly health activities processing has been triggered.",
                    messages.SUCCESS
                )
            except Exception as e:
                self.message_user(
                    request,
                    f"Error triggering workflow: {str(e)}",
                    messages.ERROR
                )
            return redirect('admin:health_activities_caloriespermonth_changelist')

        context = {
            **self.admin_site.each_context(request),
            'title': 'Trigger Monthly Processing',
        }
        return TemplateResponse(request, 'admin/trigger_processing.html', context)

