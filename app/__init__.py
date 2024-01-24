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

import sys
import logging
import os
import datetime

import uvicorn

from secrets import token_hex
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from starlette.middleware.sessions import SessionMiddleware

from py_core import logging_util
from py_core.classes.user_classes import BasicUser, verify_password
from py_core import db as database

from .auth import MANAGER, load_user
from .general_exceptions import *
from .routes import r_download_calendar, r_events, r_schedule_optimizer, r_user, r_heatmap
from . import constants


def parse_int(value, default=-1):
    try:
        return int(value)
    except:
        return default


class EZCampus_App(FastAPI):
    INSTANCE: "EZCampus_App" = None

    def __init__(self):
        FastAPI.__init__(self)

        if EZCampus_App.INSTANCE is not None:
            raise Exception(f"{self.__class__.__name__} is a singleton!")

        EZCampus_App.INSTANCE = self

        logging.info("Initializing FastAPI")
        logging.info("Loading middleware...")

        self.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.add_middleware(SessionMiddleware, secret_key=os.getenv("session_secret_key"))

        logging.info("Adding routers...")

        self.add_router(r_download_calendar.router)
        self.add_router(r_schedule_optimizer.router)
        self.add_router(r_user.router)
        self.add_router(r_heatmap.router)

        logging.info("Adding routes")
        self.add_api_route("/", self.heartbeat, methods=["GET"])
        self.add_api_route("/heartbeat", self.heartbeat, methods=["GET"])
        self.add_api_route("/root", self.root, methods=["GET"])
        self.add_api_route("/auth/token", self.docs_auth_token_login, methods=["POST"])
        self.add_api_route("/session-id", self.session_id, methods=["GET"])
        self.add_api_route("/homepage", self.homepage, methods=["GET"])

        logging.info("FastAPI ready")

    def add_router(self, router):
        logging.info(f"Adding router: {router}")

        self.include_router(router)

    async def heartbeat(self):
        raise API_200_HEARTBEAT

    async def root(self, user: BasicUser = Depends(MANAGER)):
        if user is None:
            raise API_401_UNAUTHORIZED_USER
        raise API_200_AUTHORIZED_USER

    async def docs_auth_token_login(self, form_data: OAuth2PasswordRequestForm = Depends()):
        """Auth / Login endpoint match for Swagger Docs UI"""
        user = load_user(form_data.username)

        if user is None:
            raise API_404_USER_NOT_FOUND

        if not verify_password(password=form_data.password, hashed_password=user.password):
            raise API_401_UNAUTHORIZED_USER

        access_token = MANAGER.create_access_token(
            data={"sub": user.username}, expires=datetime.timedelta(days=1)
        )

        return {"access_token": access_token, "token_type": "bearer"}

    async def session_id(self, r: Request):
        """Generate session id based on SessionMiddleware JWT.

        Notes:
            Actual JWT created by SessionMiddleware at r.cookies["session"].
        """
        if "session_id" not in r.session:
            r.session["session_id"] = token_hex(16)  # You can adjust the length of the session ID.
        return {"session_id": r.session["session_id"]}

    async def homepage(self, user: BasicUser = Depends(MANAGER)) -> dict:
        if user is None:
            raise API_404_USER_NOT_FOUND
        return {"valid": user.name}


def get_and_prase_args(args):
    import argparse

    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION]...",
        add_help=False,
    )

    general = parser.add_argument_group("General Options")
    general.add_argument(
        "-h",
        "--help",
        action="help",
        help="Print this help message and exit",
    )
    general.add_argument("-p", "--db_password", dest="db_password", help="The database password")
    general.add_argument("-u", "--db_username", dest="db_username", help="The database username")
    general.add_argument("-H", "--db_host", dest="db_host", help="The database host")
    general.add_argument("-n", "--db_name", dest="db_name", help="The database name")
    general.add_argument("-P", "--db_port", dest="db_port", help="The database port")

    general.add_argument("-d", "--host", dest="host", help="The FastAPI host")
    general.add_argument("-i", "--port", dest="port", help="The FastAPI port")

    general.add_argument(
        "-L",
        "--loglevel",
        dest="log_level",
        help=f"Set the log level, {logging_util.get_level_map_pretty()}",
    )
    general.add_argument(
        "-f",
        "--logfile",
        dest="log_file",
        help="Set the NAME of the logfile, will be put in the log directory",
    )
    general.add_argument("-D", "--logdir", dest="log_dir", help="Set the log directroy")

    return parser.parse_args(args)


def main():
    load_dotenv()

    parsed_args = get_and_prase_args(sys.argv[1:])

    time = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d_%H-%M-%S")

    log_dir = parsed_args.log_dir or os.getenv("LOG_DIR", "./logs")
    log_file = parsed_args.log_file or os.getenv("LOG_FILE", f"{constants.BRAND}{time}.log")
    log_path = os.path.join(log_dir, log_file)

    log_level = parsed_args.log_level or os.getenv("LOG_LEVEL", str(logging.INFO))
    log_level = parse_int(log_level, -1)

    assert log_level in logging_util.LOG_LEVEL_MAP, f"Unknown log level {log_level}"

    logging_util.setup_logging(log_file=log_path, log_level=log_level)
    logging_util.add_unhandled_exception_hook()

    logging.info("Starting...")
    logging.info(f"--- {constants.BRAND} ---")
    logging.info(f"--- {len(constants.BRAND) * ' '} ---")
    logging.info(f"Date Time: {time}")
    logging.info(f"Logging to {log_path}")

    if parsed_args.db_password:
        _ = parsed_args.db_password
        parsed_args.db_password = "*" * len(_)
        logging.debug(parsed_args)
        parsed_args.db_password = _
    else:
        logging.debug(parsed_args)

    if not parsed_args.db_name:
        parsed_args.db_name = str(database.get_env_db_name("ezcampus_db"))

    if not parsed_args.db_host:
        parsed_args.db_host = str(database.get_env_db_host("localhost"))

    if not parsed_args.db_password:
        parsed_args.db_password = str(database.get_env_db_password("root"))

    if not parsed_args.db_username:
        parsed_args.db_username = str(database.get_env_db_user("test"))

    if not parsed_args.db_port:
        parsed_args.db_port = int(database.get_env_db_port(3306))
    else:
        parsed_args.db_port = int(parsed_args.db_port)

    if not parsed_args.host:
        parsed_args.host = os.getenv("FASTAPI_HOST", "0.0.0.0")

    if not parsed_args.port:
        parsed_args.port = int(os.getenv("FASTAPI_PORT", 8000))
    else:
        parsed_args.port = int(parsed_args.port)

    logging.info(f"Read db hostname {parsed_args.db_host}")
    logging.info(f"Read db port {parsed_args.db_port}")
    logging.info(f"Read db name {parsed_args.db_name}")
    logging.info(f"Read db username {parsed_args.db_username}")
    logging.info(f"Read db password {'*'*len(parsed_args.db_password)}")
    logging.info(f"Read fastapi host {parsed_args.host}")
    logging.info(f"Read fastapi port {parsed_args.port}")

    database.init_database(
        use_mysql=True,
        db_port=parsed_args.db_port,
        db_host=parsed_args.db_host,
        db_name=parsed_args.db_name,
        db_user=parsed_args.db_username,
        db_pass=parsed_args.db_password,
        create=True,
    )

    EZCampus_App()

    logging.debug(EZCampus_App.INSTANCE)
    logging.info(f"Running FastAPI on host: {parsed_args.host} with port: {parsed_args.port}")

    uvicorn.run(EZCampus_App.INSTANCE, host=parsed_args.host, port=parsed_args.port)
