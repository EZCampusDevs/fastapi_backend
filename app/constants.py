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

"""Constants related to app backend computation."""

BRAND = "FastAPI Backend"
BRAND_LONG = "Scheduleplatform-" + BRAND

# ICS Calendar base file name:
BASE_ICS_FILENAME = "calendar.ics"

# Notion CSV Calendar/Database file name:
BASE_NOTION_CSV_FILENAME = "notion_csv.csv"

# Student Availability Heatmap files
HEATMAP_CSV = "ezcampus_heatmap.csv"
HEATMAP_XLSX = "ezcampus_heatmap.xlsx"
HEATMAP_XLSX_DEFAULT_SHEET = "Heatmap"

# Cache directory:
CACHE_DIR = "cache/"
