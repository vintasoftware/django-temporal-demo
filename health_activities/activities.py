from datetime import datetime
from typing import List

from asgiref.sync import sync_to_async
from temporalio import activity


def _get_users_with_activities_sync(beginning_of_month: datetime) -> List[int]:
    from django.contrib.auth.models import User
    
    return list(
        User.objects.filter(
            health_activities__created_at__gte=beginning_of_month
        ).distinct().values_list('id', flat=True)
    )

@activity.defn
async def get_users_with_activities_this_month() -> List[int]:
    now = datetime.now()
    beginning_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return await sync_to_async(_get_users_with_activities_sync)(beginning_of_month)

@activity.defn
async def process_user_health_activities(user_id: int) -> None:
    from django.contrib.auth.models import User
    from django.core.mail import send_mail
    from django.db.models import Q, Sum

    from health_activities.services import HealthActivitiesService
    
    now = datetime.now()
    beginning_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    try:
        user = await sync_to_async(User.objects.annotate(
            calories_burnt_this_moth=Sum(
                'health_activities__calories_burned',
                filter=Q(
                    health_activities__created_at__gte=beginning_of_month
                )
            )
        ).get)(id=user_id)
    except User.DoesNotExist:
        return
    
    calories_record = await sync_to_async(HealthActivitiesService().compile_latest_month_for_user)(user)

    if not calories_record:
        return

    await sync_to_async(send_mail)(
        'Health Activities Processed',
        f'Your health activities for this month have been processed. Total calories: {calories_record.calories}',
        'noreply@healthanalytics.com',
        [user.email],
        fail_silently=False,
    )

@activity.defn
async def send_admin_notification() -> None:
    from django.core.mail import send_mail

    await sync_to_async(send_mail)(
        'Monthly Health Activities Processing Complete',
        'The health activities processing for all users has been completed successfully.',
        'noreply@healthanalytics.com',
        ['hugo@vinta.com.br'],
        fail_silently=False,
    )
