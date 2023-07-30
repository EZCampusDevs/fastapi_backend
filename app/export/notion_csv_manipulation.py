import csv

"""Create csv calendar file from a list of Course objects.

Config objects' universal event attributes are utilized to generate universal events.
"""

from uuid import uuid4

from app.cache_path_manipulation import get_cache_path
from app.constants import BASE_NOTION_CSV_FILENAME
from py_core.classes.course_class import Course, course_to_extended_meetings
from py_core.classes.extended_meeting_class import ExtendedMeeting, to_single_occurrences


def create_notion_csv(source_list: list[ExtendedMeeting | Course]) -> str:
    """Create ics file given a source list.

    Args:
        source_list: List of ExtendedMeeting or Course objects to translate into ics calendar.

    Returns:
        Cache file path of the created ics file.
    """
    if not source_list:
        raise ValueError("source_list is empty")

    csv_rows = [["Title", "Datetime", "Location", "Description"]]

    for source in source_list:  # Generate event components according to source type.
        if isinstance(source, Course):
            extended_meeting_list = course_to_extended_meetings(course_list=[source])
            for ex_mt in extended_meeting_list:
                csv_rows += convert_for_notion(ex_mt)
        elif isinstance(source, ExtendedMeeting):
            csv_rows += convert_for_notion(source)
        else:
            raise TypeError(f"Expected type ExtendedMeeting or Course, received {type(source)}")

    file_path = get_cache_path(file_name=BASE_NOTION_CSV_FILENAME, cache_id=str(uuid4()))

    with open(file_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(csv_rows)
    return file_path


def convert_for_notion(ex_mt: ExtendedMeeting) -> list[list[str]]:
    single_occurrences = to_single_occurrences(ex_mt)

    csv_rows = []
    for i, mt in enumerate(single_occurrences):
        modified = mt.copy(update={"name": f"{mt.name} - {i + 1} of {len(single_occurrences)}"})
        csv_rows.append(__build_from_ex_meeting(ex_mt=modified))

    return csv_rows


def __build_from_ex_meeting(ex_mt: ExtendedMeeting) -> list[str]:
    """Translate an ExtendedMeeting to a list for later csv file writing.
    Args:
        ex_mt: ExtendedMeeting to translate.

    Returns:
        Translated list.
    """
    NOTION_DT = "%Y/%m/%d %H:%M"

    return [
        ex_mt.name,
        f"{ex_mt.dt_start().strftime(NOTION_DT)} ({ex_mt.timezone_str}) → "
        f"{ex_mt.dt_end().strftime(NOTION_DT)}",
        ex_mt.location,
        ex_mt.description,
    ]
