import asyncio
from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy
from temporalio.workflow import execute_activity

with workflow.unsafe.imports_passed_through():
    from health_activities.activities import (
        get_users_with_activities_this_month,
        process_user_health_activities,
        send_admin_notification,
    )


@workflow.defn
class ProcessMonthlyHealthActivitiesWorkflow:
    @workflow.run
    async def run(self) -> None:
        # Get all users with activities this month
        user_ids = await execute_activity(
            get_users_with_activities_this_month,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(maximum_attempts=3),
        )

        # Wait for all processing tasks to complete using workflow.wait_all
        await asyncio.gather(*(
            execute_activity(
                process_user_health_activities,
                args=[user_id],
                start_to_close_timeout=timedelta(minutes=5),
                retry_policy=RetryPolicy(maximum_attempts=3),
            )
            for user_id in user_ids
        ))

        # Send completion email to admin
        await execute_activity(
            send_admin_notification,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(maximum_attempts=3),
        )
