from datetime import timedelta

from django.core import mail
from freezegun import freeze_time

from elk.utils.testing import TestCase, create_customer
from market.models import Subscription
from products import models as products
from timeline.tasks import student_subscription_reminder


@freeze_time('2022-05-30 12:00')
class TestSubscriptionNotice(TestCase):
    fixtures = ('lessons', 'products')
    TEST_PRODUCT_ID = 1

    @classmethod
    def setUpTestData(cls):
        cls.product = products.Product1.objects.get(pk=cls.TEST_PRODUCT_ID)
        cls.product.duration = timedelta(days=48)
        cls.product.save()

        cls.customer = create_customer()

        cls.subscription: Subscription = Subscription(
            customer=cls.customer,
            product=cls.product,
            buy_price=150,
        )
        cls.subscription.save()

    def test_send_reminder(self):
        with freeze_time('2022-06-7 12:00'):
            student_subscription_reminder()
            self.assertEqual(len(mail.outbox), 1)

    def test_do_not_repeat_send_reminder(self):
        with freeze_time('2022-06-7 12:00'):
            for _ in range(5):
                student_subscription_reminder()
                self.subscription.set_last_reminder_date()
            self.assertEqual(len(mail.outbox), 1)

    def test_not_send_reminder_if_last_reminder_date_in_last_week(self):
        self.subscription.last_reminder_date = self.tzdatetime(2022, 6, 6, 12, 0)
        self.subscription.save()
        with freeze_time('2022-06-7 12:00'):
            student_subscription_reminder()
            self.assertEqual(len(mail.outbox), 0)

    def test_not_send_reminder_after_48_days(self):
        with freeze_time('2022-07-17 12:00'):
            student_subscription_reminder()
            self.assertEqual(len(mail.outbox), 0)

    def test_change_last_reminder_date(self):
        with freeze_time('2022-06-7 12:00'):
            student_subscription_reminder()
            self.subscription.set_last_reminder_date()
            self.assertEqual(self.subscription.last_reminder_date, self.tzdatetime('UTC', 2022, 6, 7, 12, 0))
