from datetime import timedelta

from elk.celery import app as celery
from market.models import Class, Subscription
from timeline.signals import class_starting_student, class_starting_teacher, subscription_money_is_running_out


@celery.task
def notify_15min_to_class():
    for i in Class.objects.starting_soon(timedelta(minutes=30)).filter(pre_start_notifications_sent_to_teacher=False).distinct('timeline'):
        for other_class_with_the_same_timeline in Class.objects.starting_soon(timedelta(minutes=30)).filter(timeline=i.timeline):
            """
            Set all other starting classes as notified either.
            """
            other_class_with_the_same_timeline.pre_start_notifications_sent_to_teacher = True
            other_class_with_the_same_timeline.save()
        class_starting_teacher.send(sender=notify_15min_to_class, instance=i)

    for i in Class.objects.starting_soon(timedelta(minutes=30)).filter(pre_start_notifications_sent_to_student=False):
        i.pre_start_notifications_sent_to_student = True
        i.save()
        class_starting_student.send(sender=notify_15min_to_class, instance=i)


@celery.task
def student_subscription_reminder():
    for item in Subscription.objects.subscriptions_not_used_for_a_week():
        if item:
            subscription_money_is_running_out.send(sender=student_subscription_reminder, instance=item)
            item.set_last_reminder_date()
