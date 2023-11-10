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

""""Experimental endpoints."""

import datetime as dt
from enum import Enum

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

from py_core.classes.extended_meeting_class import ExtendedMeeting
from py_core.classes.extended_meeting_class import http_format
from py_core.logging_util import log_endpoint

# BAD PRACTICE CODE CALLS
from datetime import date
from py_core.db import SessionObj
from py_core.db import db_globals as DG
from py_core.db import db_tables as DT

router = APIRouter(prefix="/fyic2023", tags=["fyic2023"])


class ConferenceStream(str, Enum):
    Leadership = "Leadership"  # 3
    Sustainability = "Sustainability"  # 4
    Vpx = "VPX"  # 5


class ConferenceInfoStream(BaseModel):
    stream: ConferenceStream


# FYIC Events
"""
general_events = [
    ExtendedMeeting(
        name="Check-in & Snacks",
        description="",
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(15, 0),
        time_end=dt.time(17, 0),
        date_start=dt.date(2023, 11, 10),
        date_end=dt.date(2023, 11, 10),
        timezone_str="America/Toronto",
        location="",
    ),
    ExtendedMeeting(
        name="Bus to North Campus",
        description="",
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(17, 0),
        time_end=dt.time(17, 30),
        date_start=dt.date(2023, 11, 10),
        date_end=dt.date(2023, 11, 10),
        timezone_str="America/Toronto",
        location="",
    ),
    ExtendedMeeting(
        name="Opening Ceremonies & EDI Training",
        description="",
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(17, 30),
        time_end=dt.time(19, 0),
        date_start=dt.date(2023, 11, 10),
        date_end=dt.date(2023, 11, 10),
        timezone_str="America/Toronto",
        location="SHA Atrium",
    ),
    ExtendedMeeting(
        name="Dinner at 2200 North",
        description="",
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(19, 0),
        time_end=dt.time(20, 0),
        date_start=dt.date(2023, 11, 10),
        date_end=dt.date(2023, 11, 10),
        timezone_str="America/Toronto",
        location="2200 North",
    ),
    ExtendedMeeting(
        name="Ice Skating and Trivia/Karaoke",
        description="",
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(20, 0),
        time_end=dt.time(22, 30),
        date_start=dt.date(2023, 11, 10),
        date_end=dt.date(2023, 11, 10),
        timezone_str="America/Toronto",
        location="Campus Ice Centre + 2200 North",
    ),
    ExtendedMeeting(
        name="Bus back to the Hotel",
        description="",
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(22, 30),
        time_end=dt.time(23, 0),
        date_start=dt.date(2023, 11, 10),
        date_end=dt.date(2023, 11, 10),
        timezone_str="America/Toronto",
        location="",
    ),
    ExtendedMeeting(
        name="Breakfast",
        description="",
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(8, 0),
        time_end=dt.time(9, 30),
        date_start=dt.date(2023, 11, 11),
        date_end=dt.date(2023, 11, 11),
        timezone_str="America/Toronto",
        location="",
    ),
    ExtendedMeeting(
        name="Walk to Charles Hall",
        description="",
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(9, 30),
        time_end=dt.time(10, 0),
        date_start=dt.date(2023, 11, 11),
        date_end=dt.date(2023, 11, 11),
        timezone_str="America/Toronto",
        location="",
    ),
    ExtendedMeeting(
        name="Remembrance Day Ceremony",
        description="",
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(11, 0),
        time_end=dt.time(11, 30),
        date_start=dt.date(2023, 11, 11),
        date_end=dt.date(2023, 11, 11),
        timezone_str="America/Toronto",
        location="CHA Atrium",
    ),
    ExtendedMeeting(
        name="Lunch",
        description="",
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(13, 30),
        time_end=dt.time(14, 30),
        date_start=dt.date(2023, 11, 11),
        date_end=dt.date(2023, 11, 11),
        timezone_str="America/Toronto",
        location="CHA Atrium",
    ),
    ExtendedMeeting(
        name="Prep Time for Formal",
        description="",
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(17, 30),
        time_end=dt.time(18, 30),
        date_start=dt.date(2023, 11, 11),
        date_end=dt.date(2023, 11, 11),
        timezone_str="America/Toronto",
        location="",
    ),
    ExtendedMeeting(
        name="Formal Dinner at Charles Hall",
        description="",
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(18, 30),
        time_end=dt.time(19, 30),
        date_start=dt.date(2023, 11, 11),
        date_end=dt.date(2023, 11, 11),
        timezone_str="America/Toronto",
        location="Charles Hall",
    ),
    ExtendedMeeting(
        name="Gala",
        description="",
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(18, 30),
        time_end=dt.time(19, 30),
        date_start=dt.date(2023, 11, 11),
        date_end=dt.date(2023, 11, 11),
        timezone_str="America/Toronto",
        location="Charles Hall",
    ),
    ExtendedMeeting(
        name="Walk back to the Hotel",
        description="",
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(22, 30),
        time_end=dt.time(23, 0),
        date_start=dt.date(2023, 11, 10),
        date_end=dt.date(2023, 11, 10),
        timezone_str="America/Toronto",
        location="",
    ),
    ExtendedMeeting(
        name="Breakfast",
        description="",
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(8, 0),
        time_end=dt.time(9, 30),
        date_start=dt.date(2023, 11, 12),
        date_end=dt.date(2023, 11, 12),
        timezone_str="America/Toronto",
        location="",
    ),
    ExtendedMeeting(
        name="Bus to North Campus",
        description="",
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(9, 30),
        time_end=dt.time(10, 0),
        date_start=dt.date(2023, 11, 12),
        date_end=dt.date(2023, 11, 12),
        timezone_str="America/Toronto",
        location="",
    ),
    ExtendedMeeting(
        name="Closing Ceremonies",
        description="",
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(13, 0),
        time_end=dt.time(14, 0),
        date_start=dt.date(2023, 11, 12),
        date_end=dt.date(2023, 11, 12),
        timezone_str="America/Toronto",
        location="",
    ),
    ExtendedMeeting(
        name="Lunch",
        description="",
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(14, 0),
        time_end=dt.time(15, 0),
        date_start=dt.date(2023, 11, 12),
        date_end=dt.date(2023, 11, 12),
        timezone_str="America/Toronto",
        location="",
    ),
    ExtendedMeeting(
        name="Departures",
        description="",
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(15, 0),
        time_end=dt.time(17, 30),
        date_start=dt.date(2023, 11, 12),
        date_end=dt.date(2023, 11, 12),
        timezone_str="America/Toronto",
        location="",
    ),
]

stream1_events = [
    ExtendedMeeting(
        name="Strategic Blueprint: Building a Goal-Oriented Future",
        description="",
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(10, 0),
        time_end=dt.time(11, 0),
        date_start=dt.date(2023, 11, 11),
        date_end=dt.date(2023, 11, 11),
        timezone_str="America/Toronto",
        location="CHA 216",
    ),
    ExtendedMeeting(
        name="Empathy & Efficiency: Compassionate Conversations",
        description="",
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(11, 30),
        time_end=dt.time(12, 30),
        date_start=dt.date(2023, 11, 11),
        date_end=dt.date(2023, 11, 11),
        timezone_str="America/Toronto",
        location="CHA 216",
    ),
    ExtendedMeeting(
        name="Choose your own adventure: Student Edition",
        description="",
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(12, 30),
        time_end=dt.time(13, 30),
        date_start=dt.date(2023, 11, 11),
        date_end=dt.date(2023, 11, 11),
        timezone_str="America/Toronto",
        location="CHA 216",
    ),
    ExtendedMeeting(
        name="Oh Crap! Now What? - Transforming Crisis to Confidence",
        description="",
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(14, 30),
        time_end=dt.time(15, 30),
        date_start=dt.date(2023, 11, 11),
        date_end=dt.date(2023, 11, 11),
        timezone_str="America/Toronto",
        location="CHA 216",
    ),
    ExtendedMeeting(
        name="ESSCO 101 & CFES 101",
        description="",
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(15, 30),
        time_end=dt.time(16, 30),
        date_start=dt.date(2023, 11, 11),
        date_end=dt.date(2023, 11, 11),
        timezone_str="America/Toronto",
        location="CHA 213",
    ),
    ExtendedMeeting(
        name="Teamwork & Collaboration",
        description="",
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(15, 30),
        time_end=dt.time(16, 30),
        date_start=dt.date(2023, 11, 11),
        date_end=dt.date(2023, 11, 11),
        timezone_str="America/Toronto",
        location="CHA 216",
    ),
    ExtendedMeeting(
        name="OSPE",
        description="",
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(10, 0),
        time_end=dt.time(11, 0),
        date_start=dt.date(2023, 11, 12),
        date_end=dt.date(2023, 11, 12),
        timezone_str="America/Toronto",
        location="SIRC 2020",
    ),
    ExtendedMeeting(
        name="EngSoc",
        description="Discuss the latest initiatives and goals of the Engineering Society.",
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(11, 0),
        time_end=dt.time(12, 0),
        date_start=dt.date(2023, 11, 12),
        date_end=dt.date(2023, 11, 12),
        timezone_str="America/Toronto",
        location="SIRC 1350",
    ),
    ExtendedMeeting(
        name="How to Succeed Under Pressure and Stress",
        description="Gain insights on managing stress and excelling under pressure.",
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(12, 0),
        time_end=dt.time(13, 0),
        date_start=dt.date(2023, 11, 12),
        date_end=dt.date(2023, 11, 12),
        timezone_str="America/Toronto",
        location="SIRC 1350",
    ),
]

stream2_events = [
    ExtendedMeeting(
        name="Taking technology from the lab to the real world: Ekstra's Stirling Engines",
        description="",
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(10, 0),
        time_end=dt.time(11, 0),
        date_start=dt.date(2023, 11, 11),
        date_end=dt.date(2023, 11, 11),
        timezone_str="America/Toronto",
        location="CHA 215",
    ),
    ExtendedMeeting(
        name="Aquatic Contaminants and their Effects",
        description="",
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(11, 30),
        time_end=dt.time(12, 30),
        date_start=dt.date(2023, 11, 11),
        date_end=dt.date(2023, 11, 11),
        timezone_str="America/Toronto",
        location="CHA 215",
    ),
    ExtendedMeeting(
        name="The future of sustainable e-mobility: Challenges and Opportunities",
        description="",
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(12, 30),
        time_end=dt.time(13, 30),
        date_start=dt.date(2023, 11, 11),
        date_end=dt.date(2023, 11, 11),
        timezone_str="America/Toronto",
        location="CHA 215",
    ),
    ExtendedMeeting(
        name="Nuclear",
        description="",
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(14, 30),
        time_end=dt.time(15, 30),
        date_start=dt.date(2023, 11, 11),
        date_end=dt.date(2023, 11, 11),
        timezone_str="America/Toronto",
        location="CHA 215",
    ),
    ExtendedMeeting(
        name="ESSCO 101 & CFES 101",
        description="",
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(15, 30),
        time_end=dt.time(16, 30),
        date_start=dt.date(2023, 11, 11),
        date_end=dt.date(2023, 11, 11),
        timezone_str="America/Toronto",
        location="CHA 213",
    ),
    ExtendedMeeting(
        name="Electrification Sustainability for Generations",
        description="",
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(15, 30),
        time_end=dt.time(16, 30),
        date_start=dt.date(2023, 11, 11),
        date_end=dt.date(2023, 11, 11),
        timezone_str="America/Toronto",
        location="CHA 215",
    ),
    ExtendedMeeting(
        name="OSPE",
        description="",
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(10, 0),
        time_end=dt.time(11, 0),
        date_start=dt.date(2023, 11, 12),
        date_end=dt.date(2023, 11, 12),
        timezone_str="America/Toronto",
        location="SIRC 2020",
    ),
    ExtendedMeeting(
        name="ACE Facility Tour",
        description="Take a guided tour of the ACE Facility and explore its innovations.",
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(11, 0),
        time_end=dt.time(13, 0),
        date_start=dt.date(2023, 11, 12),
        date_end=dt.date(2023, 11, 12),
        timezone_str="America/Toronto",
        location="ACE",
    ),
]

stream3_events = [
    ExtendedMeeting(
        name="What makes ESSCO BESSCO ft. Shanleigh",
        description=(
            "What makes ESSCO so great? In this session for our VPX's, Shanleigh who has been "
            "around Canada through engineering student body government, will break it down for us "
            "and how we can show off ESSCO pride, not only at the provincial level but at the "
            "CFES level as well! We will learn about her story and how she was able to apply her "
            "skills in external activities to her life in industry now."
        ),
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(10, 0),
        time_end=dt.time(11, 0),
        date_start=dt.date(2023, 11, 11),
        date_end=dt.date(2023, 11, 11),
        timezone_str="America/Toronto",
        location="CHA 217",
    ),
    ExtendedMeeting(
        name="BOD Portfolio Updates",
        description=(
            "What time is it? BOD Updates time! Given by Pres and all the VP's, they will break "
            "down what they've been up to and what they have planned for the future to all the "
            "VPX's. BOD will explain how they've been trying to improve their roles, different "
            "projects they have in store and speak about what their commissioners have been "
            "working on as well."
        ),
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(11, 30),
        time_end=dt.time(12, 30),
        date_start=dt.date(2023, 11, 11),
        date_end=dt.date(2023, 11, 11),
        timezone_str="America/Toronto",
        location="CHA 217",
    ),
    ExtendedMeeting(
        name="Advocacy Portfolio Review + Roundtables",
        description=(
            "The one, the only, OMAR! In this session for our VPX's our VP Advocacy will break "
            "down all the great work that he has been working on and what he plans on doing in "
            "the future. Utilizing a collaborative space, Omar is seeking to get input on what "
            "students across Ontario seek advocacy on."
        ),
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(12, 30),
        time_end=dt.time(13, 30),
        date_start=dt.date(2023, 11, 11),
        date_end=dt.date(2023, 11, 11),
        timezone_str="America/Toronto",
        location="CHA 211",
    ),
    ExtendedMeeting(
        name="Accountability Role Review",
        description=(
            "Shiver me timbers! It's the accountability role review session! In this session, "
            "all the VPX's will have the opportunity to express their feedback and opinions of "
            "how BOD has been running this year and what they can do to be better. The VPX's will "
            "have the opportunity to do this away from BOD and only amongst themselves."
        ),
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(14, 30),
        time_end=dt.time(15, 30),
        date_start=dt.date(2023, 11, 11),
        date_end=dt.date(2023, 11, 11),
        timezone_str="America/Toronto",
        location="CHA 211",
    ),
    ExtendedMeeting(
        name="Bringing back value to your schools from conference",
        description=(
            "What does ESSCO love as much as Advocacy? Conferences! In this session, TMU VPX "
            "Aaron Segal and VP Services Rafael Saltos will break down historic data on ESSCO "
            "conferences, and what schools are doing to ensure that their delegates are bringing "
            "back knowledge and information from these conferences. In addition, talking about "
            "how students can get to know more about ESSCO earlier and get more involved."
        ),
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(15, 30),
        time_end=dt.time(16, 30),
        date_start=dt.date(2023, 11, 11),
        date_end=dt.date(2023, 11, 11),
        timezone_str="America/Toronto",
        location="CHA 217",
    ),
    ExtendedMeeting(
        name="Motion Writing",
        description=(
            "No more fun session!? Are you serious!? During this time period, VPX's will have the "
            "opportunity to write motions for Sunday's plenary."
        ),
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(15, 30),
        time_end=dt.time(16, 30),
        date_start=dt.date(2023, 11, 11),
        date_end=dt.date(2023, 11, 11),
        timezone_str="America/Toronto",
        location="TBD - Charles Hall?",
    ),
    ExtendedMeeting(
        name="Plenary",
        description="",
        seats_filled=0,
        max_capacity=-1,
        is_virtual=False,
        colour=None,
        time_start=dt.time(10, 0),
        time_end=dt.time(13, 0),
        date_start=dt.date(2023, 11, 12),
        date_end=dt.date(2023, 11, 12),
        timezone_str="America/Toronto",
        location="SIRC 3110",
    ),
]
"""


# ########## START OF BAD PRACTICE CODE / PATCH ##########
# THIS IS BAD PRACTICE, URGENT PATCH FOR FYIC DUE TO RELATED EFFECTS OF py_core ISSUE #13.
# CODE BASED OFF def get_users_via( ... IN py_core user.py.
def get_fyic_events_via_colour(colour: list[int] | None = None) -> list[ExtendedMeeting]:
    if colour is None or not colour:
        return []

    session: SessionObj
    try:
        with DG.Session.begin() as session:
            result = session.query(DT.TBL_Event).filter(
                DT.TBL_Event.color.in_(colour),
            )
            return [
                ExtendedMeeting(
                    time_start=r.begin_time,
                    time_end=r.end_time,
                    date_start=r.started_at,
                    date_end=r.ended_at,
                    timezone_str=r.timezone,
                    occurrence_unit=r.occurrence_unit,
                    occurrence_interval=r.occurrence_interval,
                    occurrence_limit=(
                        r.occurrence_until
                        if isinstance(r.occurrence_until, date)
                        else r.occurrence_repeat  # int based limit.
                    ),
                    days_of_week=r.days_of_week,
                    location=r.location,
                    name=r.name,
                    description=r.description,
                    seats_filled=r.seats_filled,
                    max_capacity=r.max_capacity,
                    is_virtual=r.is_virtual,
                    colour=None,  # Override colour (due to pycore issue #13).
                )
                for r in result
            ]
    except AttributeError as e:
        msg = e.args[0]
        if "'NoneType' object has no attribute 'begin'" in msg:
            raise RuntimeWarning(
                f"{msg} <--- Daniel: Check (local / ssh) connection to DB, possible missing "
                f"init_database() call via 'from py_core.db import init_database'"
            )
        else:
            raise e
    except Exception as e:
        raise e


# ########## END OF BAD PRACTICE CODE / PATCH ##########


@router.post("/events")
async def events(r: Request, r_model: ConferenceInfoStream):
    general_events = get_fyic_events_via_colour([1])
    all_events = general_events.copy()

    if r_model.stream == ConferenceStream.Vpx:
        all_events += get_fyic_events_via_colour([5])
    elif r_model.stream == ConferenceStream.Sustainability:
        all_events += get_fyic_events_via_colour([4])
    else:  # r_model.stream == ConferenceStream.Leadership
        all_events += get_fyic_events_via_colour([3])

    formatted = http_format(all_events)
    h = HTTPException(status.HTTP_200_OK, formatted)
    log_endpoint(h, r)
    return HTTPException(status.HTTP_200_OK, formatted)
