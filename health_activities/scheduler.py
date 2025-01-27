import uuid
from datetime import datetime, timedelta

from temporalio.client import (
    Schedule,
    ScheduleActionStartWorkflow,
    ScheduleCalendarSpec,
    ScheduleSpec,
)

from health_activities.workflows import ProcessMonthlyHealthActivitiesWorkflow


async def create_monthly_health_activities_schedule(client):
    await client.create_schedule(
        'process-monthly-health-activities',
        Schedule(
            action=ScheduleActionStartWorkflow(
                ProcessMonthlyHealthActivitiesWorkflow.run,
                id=f"health-activities-compilation-{datetime.now().isoformat()}-{str(uuid.uuid4())}",
                task_queue='health-activities',
            ),
            spec=ScheduleSpec(
                # Run on day 5 of every month
                workflow=ProcessMonthlyHealthActivitiesWorkflow.run,
                calendars=[
                    ScheduleCalendarSpec(
                        month='*',
                        day_of_month='5',
                        hour='0',
                        minute='0',
                    )
                ],
                jitter=timedelta(minutes=5),  # Add some randomness to prevent exact same time execution
            ),
        ),
    )
