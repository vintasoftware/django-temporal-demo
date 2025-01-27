import datetime

from django.contrib.auth.models import User
from django.db.models import Q, Sum
from django.db.models.functions import TruncMonth

from health_activities.models import CaloriesPerMonth, HealthActivity


class HealthActivitiesService:

    def compile_latest_month_for_user(self, user: User) -> CaloriesPerMonth | None:
        """
        Compile the total calories burned by the user for each month.
        """

        now = datetime.datetime.now()
        beginning_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month = beginning_of_month.month
        year = beginning_of_month.year

        if hasattr(user, "calories_burnt_this_moth"):
            total_calories = user.calories_burnt_this_moth

        else:
            # Get all health activities for the user
            health_activities = HealthActivity.objects.filter(
                user=user, 
                created_at__gte=beginning_of_month
            )

            # Group by month and year, and sum the calories burned
            last_month_calories_record = (
                health_activities
                .annotate(month=TruncMonth('created_at'))
                .values('month')
                .annotate(total_calories=Sum('calories_burned'))
            )

            if not last_month_calories_record:
                return None
            
            last_month_calories = last_month_calories_record[0]['total_calories']
            total_calories = last_month_calories

        return CaloriesPerMonth.objects.update_or_create(
            user=user,
            month=month,
            year=year,
            defaults={'calories': total_calories}
        )[0]
