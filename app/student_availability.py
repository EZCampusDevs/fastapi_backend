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

"""Student Availability module."""

import csv
from datetime import date

import numpy as np
import pandas as pd
from openpyxl.formatting.rule import ColorScaleRule

from app.cache_path_manipulation import get_cache_path
from constants import HEATMAP_CSV, HEATMAP_XLSX, HEATMAP_XLSX_DEFAULT_SHEET
from py_core.classes.course_class import Course, course_to_extended_meetings
from py_core.classes.extended_meeting_class import ExtendedMeeting, to_single_occurrences
from py_core.course import get_courses_via

all_course_objects = get_courses_via(course_id_list=[])


def generate_heatmap(
    source_list: list[Course | ExtendedMeeting],
    scope_date_start: date,
    scope_date_end: date,
    scope_hour_start: int,
    scope_hour_end: int,
    save_as_csv: bool = False,
    save_as_xlsx: bool = False,
) -> dict[str, str]:
    """Generate student availability heatmap in csv and / or xlsx file types.

    Args:
        source_list: List of Course and ExtendedMeeting objects.
        scope_date_start: Scope start date (inclusive).
        scope_hour_start: Scope start in hours, range [0, 23].
        scope_date_end: Scope end date (inclusive).
        scope_hour_end: Scope end in hours, range [0, 23].
        save_as_csv: Boolean to decide to save as csv file format. Default is False.
        save_as_xlsx: Boolean to decide to save as xlsx file format. Default is False.

    Returns:
        Dictionary of saved filetypes, {"csv": "csv_filepath", "xlsx": "xlsx_filepath"}
    """
    # ---------- Start of initial data checks ----------
    if not (scope_date_start <= scope_date_end):
        raise ValueError(
            f"Expected scope_date_start={scope_date_start} <= " f"scope_date_end={scope_date_end}"
        )
    if not (0 <= scope_hour_start <= 23):
        raise ValueError(f"Expected 0 <= scope_hour_start={scope_hour_start} <= 23")
    if not (0 <= scope_hour_end <= 23):
        raise ValueError(f"Expected 0 <= scope_hour_end={scope_hour_end} <= 23")
    if not (scope_hour_start < scope_hour_end):
        raise ValueError(
            f"Expected scope_time_start={scope_hour_start} < scope_time_end={scope_hour_end}"
        )
    # ---------- End of initial data checks ----------

    # ---------- Start of source_list conversions ----------
    single_ex_mts = []  # Single occurrence ExtendedMeetings.
    for s in source_list:
        if isinstance(s, Course):
            for m in course_to_extended_meetings([s]):
                single_ex_mts += to_single_occurrences(m)
        elif isinstance(s, ExtendedMeeting):
            single_ex_mts += to_single_occurrences(s)
        else:
            raise TypeError(f"Expected type ExtendedMeeting or Course, received {type(s)}")
    # ---------- End of source_list conversions ----------

    # ---------- Start of numpy calculations ----------
    # Calculate number of days and samples.
    num_days = (scope_date_end - scope_date_start).days + 1
    num_intervals = 2 * (scope_hour_end - scope_hour_start)  # 30 minute intervals.

    # Create a 2D numpy array.
    calc = np.zeros((num_days, num_intervals), dtype=int)

    # Iterate over the events and update the calc array.
    for ex_mt in single_ex_mts:
        if (
            scope_date_start <= ex_mt.date_start <= scope_date_end
            or scope_date_start <= ex_mt.date_end <= scope_date_end
        ):  # Only process if within the scope dates.
            # Calculating start and end date indexes.
            day_start_idx = (ex_mt.date_start - scope_date_start).days
            day_end_idx = (ex_mt.date_end - scope_date_start).days

            # Converting hour and minute to half-hour interval index.
            time_start_idx = (
                2 * (ex_mt.time_start.hour - scope_hour_start) + ex_mt.time_start.minute // 30
            )
            time_end_idx = (
                2 * (ex_mt.time_end.hour - scope_hour_start) + ex_mt.time_end.minute // 30 - 1
            )

            # Update the array for where the class occurs.
            calc[
                day_start_idx : day_end_idx + 1, time_start_idx : time_end_idx + 1
            ] += ex_mt.seats_filled

    # Save the array to a CSV file.
    # Adding headers for times and a sidebar for dates.
    headers = [
        f"{i//2:02}:{i%2*30:02}-{(i+1)//2:02}:{(i+1)%2*30:02}"
        for i in range(scope_hour_start * 2, scope_hour_end * 2)
    ]
    headers = ["Date/Time"] + headers  # Adding label for the first column.

    # Convert the calc array to a list of lists to facilitate modifications
    calc_list = calc.tolist()

    cache_paths = {}  # Store all cache paths for generated files.
    # ---------- End of numpy calculations ----------

    # ---------- Start of heatmap file export ----------
    if save_as_csv or save_as_xlsx:
        # Inserting the dates on the left sidebar
        for idx, d in enumerate(
            range(scope_date_start.toordinal(), scope_date_end.toordinal() + 1)
        ):
            curr_date = date.fromordinal(d)
            calc_list[idx] = [curr_date.isoformat()] + calc_list[idx]

    # Export to csv.
    if save_as_csv:
        # Save the array to a csv file
        file_path = get_cache_path(file_name=HEATMAP_CSV)  # Get internal cache path.
        with open(file_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(headers)  # Write the headers first
            for row in calc_list:  # Write the rest of the data
                writer.writerow(row)

        cache_paths["csv"] = file_path  # Save as valid cache path.

    # Export to xlsx (excel) file.
    if save_as_xlsx:
        # 1. Convert the DataFrame to an ExcelWriter object.
        df = pd.DataFrame(calc_list, columns=headers)  # Create dataframe.
        file_path = get_cache_path(file_name=HEATMAP_XLSX)  # Get internal cache path.
        writer = pd.ExcelWriter(file_path, engine="openpyxl")
        df.to_excel(writer, sheet_name=HEATMAP_XLSX_DEFAULT_SHEET, index=False)
        ws = writer.sheets[HEATMAP_XLSX_DEFAULT_SHEET]  # default sheet name

        # 2. Use openpyxl to access the sheet and then apply conditional formatting.
        color_scale_rule = ColorScaleRule(
            start_type="min",
            start_color="008000",
            mid_type="percentile",
            mid_value=50,
            mid_color="FFFF00",
            end_type="max",
            end_color="FF0000",
        )
        ws.conditional_formatting.add(f"B2:AE{ws.max_row}", color_scale_rule)

        # 3. Close and save the formatted Excel file.
        writer.close()

        cache_paths["xlsx"] = file_path  # Save as valid cache path.
    # ---------- End of heatmap file export ----------

    return cache_paths
