import asyncio

from django.conf import settings
from temporalio.client import Client, ScheduleAlreadyRunningError
from temporalio.worker import Worker

from health_activities.scheduler import create_monthly_health_activities_schedule
from health_activities.workflows import (
    ProcessMonthlyHealthActivitiesWorkflow,
    get_users_with_activities_this_month,
    process_user_health_activities,
    send_admin_notification,
)


async def run_worker():
    client = await Client.connect(settings.TEMPORAL_SERVER_URL)

    # Try to create the schedule
    try:
        await create_monthly_health_activities_schedule(client)
    except ScheduleAlreadyRunningError:
        print("Monthly health activities schedule already exists")
    except Exception as e:
        print(f"Error creating schedule: {e}")

    worker = Worker(
        client,
        task_queue="health-activities",
        workflows=[ProcessMonthlyHealthActivitiesWorkflow],
        activities=[
            get_users_with_activities_this_month,
            process_user_health_activities,
            send_admin_notification,
        ],
    )

    await worker.run()


def main():
    asyncio.run(run_worker())


if __name__ == "__main__":
    main()
