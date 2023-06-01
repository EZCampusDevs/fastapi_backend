"""Create ics calendar file from a list of Course objects.

Config objects' universal event attributes are utilized to generate universal events.
"""

from datetime import date, time, datetime
from uuid import uuid4

from cache_path_manipulation import get_cache_path
from constants import BASE_ICS_FILENAME
from py_core.classes.course_class import Course, course_to_extended_meetings
from py_core.classes.extended_meeting_class import ExtendedMeeting
from py_core.constants import OU_DAYS, OU_WEEKS, OU_MONTHS_WD, OU_MONTHS_N, OU_YEARS

DAYS = {0: "MO", 1: "TU", 2: "WE", 3: "TH", 4: "FR", 5: "SA", 6: "SU"}


def create_ics_calendar(source_list: list[ExtendedMeeting | Course]) -> str:
    """Create ics file given a source list.

    Args:
        source_list: List of ExtendedMeeting or Course objects to translate into ics calendar.

    Returns:
        Cache file path of the created ics file.
    """
    if not source_list:
        raise ValueError("source_list is empty")

    events_text = ""
    for source in source_list:  # Generate event components according to source type.
        if isinstance(source, Course):
            extended_meeting_list = course_to_extended_meetings(course_list=[source])
            for ex_mt in extended_meeting_list:
                events_text += __build_from_ex_meeting(ex_mt=ex_mt)
        elif isinstance(source, ExtendedMeeting):
            events_text += __build_from_ex_meeting(ex_mt=source)
        else:
            raise TypeError(f"Expected type ExtendedMeeting or Course, received {type(source)}")

    file_path = get_cache_path(file_name=BASE_ICS_FILENAME, cache_id=str(uuid4()))  # Cache the file.
    with open(file_path, "w") as f:
        f.write(f"BEGIN:VCALENDAR\n"
                f"PRODID:EZCampus\n"
                f"{events_text}"
                f"END:VCALENDAR")
    return file_path


def __build_from_ex_meeting(ex_mt: ExtendedMeeting) -> str:
    """Translate an ExtendedMeeting to an isc text VEVENT.
    Args:
        ex_mt: ExtendedMeeting to translate.

    Returns:
        Translated icalendar.Event.
    """

    def get_limit():
        if isinstance(ex_mt.occurrence_limit, int):
            return f"COUNT={ex_mt.occurrence_limit}"
        elif isinstance(ex_mt.occurrence_limit, date):
            return f"UNTIL={datetime.combine(ex_mt.occurrence_limit, time.max).strftime('%Y%m%dT%H%M%S')}"
        else:
            raise TypeError(f"ex_mt.occurrence_limit must be type {date} or {int}")

    dt_text = (f"DTSTART;TZID=America/Toronto:"
               f"{datetime.combine(ex_mt.date_start, ex_mt.time_start).strftime('%Y%m%dT%H%M%S')}\n"
               f"DTEND;TZID=America/Toronto:"
               f"{datetime.combine(ex_mt.date_end, ex_mt.time_end).strftime('%Y%m%dT%H%M%S')}\n")
    if ex_mt.occurrence_unit == OU_DAYS:
        dt_text += f"RRULE:FREQ=DAILY;{get_limit()};INTERVAL={ex_mt.occurrence_interval}\n"
    elif ex_mt.occurrence_unit == OU_WEEKS:
        dt_text += (f"RRULE:FREQ=WEEKLY;{get_limit()};BYDAY={','.join([DAYS[n] for n in ex_mt.decode_weekday_ints()])}"
                    f";INTERVAL={ex_mt.occurrence_interval}\n")
    elif ex_mt.occurrence_unit == OU_MONTHS_WD:
        dt_text += (f"RRULE:FREQ=MONTHLY;{get_limit()};INTERVAL={ex_mt.occurrence_interval}"
                    f";BYDAY={(ex_mt.date_start.day - 1) // 7 + 1}{DAYS[ex_mt.date_start.weekday()]}\n")
    elif ex_mt.occurrence_unit == OU_MONTHS_N:
        dt_text += (f"RRULE:FREQ=MONTHLY;{get_limit()};INTERVAL={ex_mt.occurrence_interval}"
                    f";BYMONTHDAY={ex_mt.date_start.day}\n")
    elif ex_mt.occurrence_unit == OU_YEARS:
        dt_text += f"RRULE:FREQ=YEARLY;{get_limit()};INTERVAL={ex_mt.occurrence_interval}\n"
    # if ex_mt.occurrence_unit is None, pass  # No recurrence.

    return (f"BEGIN:VEVENT\n"
            f"SUMMARY:{ex_mt.name}\n"
            f"DESCRIPTION:{ex_mt.description}\n"
            f"LOCATION:{ex_mt.location}\n"
            f"{dt_text}"
            f"END:VEVENT\n")
