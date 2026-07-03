
from datetime import timedelta

from django.db import transaction
from django.db.models import Avg

from .models import LearningSession, UserSubjectProgress, DailyActivity


@transaction.atomic
def register_session(session: LearningSession):

    _update_subject_progress(session)
    _update_daily_activity(session)
    _update_streak(session.user)


def _update_subject_progress(session: LearningSession):
    progress, _ = UserSubjectProgress.objects.get_or_create(
        user=session.user, subject=session.subject
    )
    progress.total_minutes += session.duration_minutes
    progress.sessions_count += 1
    progress.total_questions += session.total_questions
    progress.correct_answers += session.correct_answers

    if session.level_at_session:
        progress.current_level = session.level_at_session

    aggregates = LearningSession.objects.filter(
        user=session.user, subject=session.subject
    ).aggregate(
        avg_pron=Avg("pronunciation_accuracy"),
        avg_grammar=Avg("grammar_accuracy"),
    )
    progress.average_pronunciation = aggregates["avg_pron"]
    progress.average_grammar = aggregates["avg_grammar"]
    progress.save()


def _update_daily_activity(session: LearningSession):
    activity_date = session.started_at.date()
    activity, _ = DailyActivity.objects.get_or_create(
        user=session.user, date=activity_date
    )
    activity.minutes_spent += session.duration_minutes
    activity.sessions_count += 1
    activity.save()


def _update_streak(user):

    today = DailyActivity.objects.filter(user=user).order_by("-date").first()
    if not today:
        return

    last_date = today.date
    if user.last_activity_date == last_date:
        return

    if user.last_activity_date == last_date - timedelta(days=1):
        user.current_streak_days += 1
    elif user.last_activity_date == last_date:
        pass
    else:
        user.current_streak_days = 1

    user.last_activity_date = last_date
    user.longest_streak_days = max(user.longest_streak_days, user.current_streak_days)
    user.save(update_fields=[
        "current_streak_days", "longest_streak_days", "last_activity_date",
    ])
