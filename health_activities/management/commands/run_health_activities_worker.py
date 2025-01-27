import asyncio

import uvloop
from django.conf import settings
from django.core.management.base import BaseCommand
from temporalio.client import Client, ScheduleAlreadyRunningError
from temporalio.worker import Worker

from health_activities.scheduler import (
    create_monthly_health_activities_schedule,
)
from health_activities.workflows import (
    ProcessMonthlyHealthActivitiesWorkflow,
    get_users_with_activities_this_month,
    process_user_health_activities,
    send_admin_notification,
)


async def run():
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


async def get_client() -> Client | None:
    """Get the Temporal client.

    The demo has a race condition in startup between the Temporal server
    and the worker. We try to get the client in a silly while loop
    so that the demo doesn't crash on startup.
    """
    connecting = True
    client = None
    while connecting:
        try:
            client = await Client.connect("localhost:7233", namespace="default")
            connecting = False
            print("Connected to Temporal")
        except RuntimeError:
            # This code is pretty dumb. In a real context, don't try to connect forever.
            print("Failed to connect to Temporal. Retrying...")
            await asyncio.sleep(1)

    return client


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        uvloop.run(run())