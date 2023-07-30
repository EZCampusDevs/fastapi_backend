"""Create json for exporting events to Google Calendar.

Config objects' universal event attributes are utilized to generate universal events.
"""

import json

from py_core.classes.course_class import Course, course_to_extended_meetings
from py_core.classes.extended_meeting_class import ExtendedMeeting

DAYS = {0: "MO", 1: "TU", 2: "WE", 3: "TH", 4: "FR", 5: "SA", 6: "SU"}


def get_gcal_event_jsons(source_list: list[ExtendedMeeting | Course]) -> list[str]:
    """Return a list of json str for Google Calendar export.

    Args:
        source_list: List of ExtendedMeeting or Course objects to translate into json strs.

    Returns:
        List of json str for Google Calendar export.
    """
    if not source_list:
        raise ValueError("source_list is empty")

    event_body_strs = []
    for source in source_list:  # Generate event components according to source type.
        if isinstance(source, Course):
            extended_meeting_list = course_to_extended_meetings(course_list=[source])
            for ex_mt in extended_meeting_list:
                event_body_strs.append(__build_from_ex_meeting(ex_mt=ex_mt))
        elif isinstance(source, ExtendedMeeting):
            event_body_strs.append(__build_from_ex_meeting(ex_mt=source))
        else:
            raise TypeError(f"Expected type ExtendedMeeting or Course, received {type(source)}")

    return event_body_strs


def __build_from_ex_meeting(ex_mt: ExtendedMeeting) -> str:
    """Translate an ExtendedMeeting to an isc text VEVENT.
    Args:
        ex_mt: ExtendedMeeting to translate.

    Returns:
        Translated icalendar.Event.
    """
    rrule_str = str(ex_mt.get_rrule())[str(ex_mt.get_rrule()).index("RRULE:"):]

    return json.dumps(
        {
            "summary": ex_mt.name,
            "location": ex_mt.location,
            "description": ex_mt.description,
            "start": {
                "dateTime": ex_mt.dt_start().isoformat(),
                "timeZone": ex_mt.timezone_str,
            },
            "end": {
                "dateTime": ex_mt.dt_end().isoformat(),
                "timeZone": ex_mt.timezone_str,
            },
            "recurrence": [rrule_str],
        }
    )
