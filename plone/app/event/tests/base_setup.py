from datetime import datetime
from datetime import timedelta
from plone.app.event.testing import set_browserlayer
from plone.app.event.testing import set_timezone
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

import unittest2 as unittest
import pytz

TEST_TIMEZONE = 'Europe/Vienna'


def patched_now(context=None):
    """Patch localized_now to allow stable results in tests.
    """
    if not context:
        context = None
    tzinfo = pytz.timezone(TEST_TIMEZONE)
    now = datetime(2013, 5, 5, 10, 0, 0).replace(microsecond=0)
    now = tzinfo.localize(now)  # set tzinfo with correct DST offset
    return now


class AbstractSampleDataEvents(unittest.TestCase):
    layer = None  # Set the plone.app.testing layer in concrete implementation

    def event_factory(self):
        # Return the IEventAccessor.create event factory.
        raise NotImplementedError

    def make_dates(self):
        tz = pytz.timezone(TEST_TIMEZONE)
        now = self.now = patched_now()
        past = self.past = tz.normalize(now - timedelta(days=10))
        future = self.future = tz.normalize(now + timedelta(days=10))
        far = self.far = tz.normalize(now + timedelta(days=30))
        duration = self.duration = timedelta(hours=1)
        return (now, past, future, far, duration)

    def setUp(self):
        self.portal = self.layer['portal']
        self.app = self.layer['app']
        self.request = self.layer['request']
        set_browserlayer(self.request)
        set_timezone(TEST_TIMEZONE)

        now, past, future, far, duration = self.make_dates()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        factory = self.event_factory()
        self.past_event = factory(
            container=self.portal,
            content_id='past',
            title=u'Past Event',
            start=past,
            end=past + duration,
            location=u"Vienna",
            whole_day=True,
            timezone=TEST_TIMEZONE,
            recurrence='RRULE:FREQ=DAILY;COUNT=3',
            ).context

        self.now_event = factory(
            container=self.portal,
            content_id='now',
            title=u'Now Event',
            start=now,
            end=now + duration,
            location=u"Vienna",
            timezone=TEST_TIMEZONE,
            recurrence="""RRULE:FREQ=DAILY;COUNT=3;INTERVAL=1
RDATE:20130509T000000
EXDATE:20130506T000000,20140404T000000""",
            contact_name='Auto Testdriver',
            contact_email='testdriver@plone.org',
            contact_phone='+123456789',
            event_url='http://plone.org',
            subjects=['plone', 'testing']).context

        self.future_event = factory(
            container=self.portal,
            content_id='future',
            title=u'Future Event',
            start=future,
            end=future + duration,
            location=u'Graz',
            timezone=TEST_TIMEZONE).context

        self.portal.invokeFactory('Folder', 'sub', title=u'sub')
        self.long_event = factory(
            container=self.portal.sub,
            content_id='long',
            title=u'Long Event',
            start=past,
            end=far,
            location=u'Schaftal',
            timezone=TEST_TIMEZONE).context
