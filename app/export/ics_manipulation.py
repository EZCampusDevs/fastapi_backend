# Copyright (C) 2022-2023 EZCampus 
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Create ics calendar file from a list of Course objects.

Config objects' universal event attributes are utilized to generate universal events.
"""

from app.cache_path_manipulation import get_cache_path
from app.constants import BASE_ICS_FILENAME
from py_core.classes.course_class import Course, course_to_extended_meetings
from py_core.classes.extended_meeting_class import ExtendedMeeting

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
            raise TypeError(
                f"Expected type ExtendedMeeting or Course, received {type(source)}"
            )

    file_path = get_cache_path(file_name=BASE_ICS_FILENAME)
    with open(file_path, "w") as f:
        f.write(
            f"BEGIN:VCALENDAR\n" f"PRODID:EZCampus\n" f"{events_text}" f"END:VCALENDAR"
        )
    return file_path


def __build_from_ex_meeting(ex_mt: ExtendedMeeting) -> str:
    """Translate an ExtendedMeeting to an isc text VEVENT.
    Args:
        ex_mt: ExtendedMeeting to translate.

    Returns:
        Translated ics VEVENT string.
    """
    return (
        f"BEGIN:VEVENT\n"
        f"SUMMARY:{ex_mt.name}\n"
        f"DESCRIPTION:{ex_mt.raw_new_line_description()}\n"
        f"LOCATION:{ex_mt.location}\n"
        f"{ex_mt.get_ics_rrule_str()}\n"
        f"END:VEVENT\n"
    )
