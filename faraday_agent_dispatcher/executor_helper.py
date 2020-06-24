# Copyright (C) 2019  Infobyte LLC (http://www.infobytesec.com/)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json
from json import JSONDecodeError

from faraday_agent_dispatcher import logger as logging
from faraday_agent_dispatcher.config import instance as config
from faraday_agent_dispatcher.utils.text_utils import Bcolors
from faraday_agent_dispatcher.utils.url_utils import api_url

from aiohttp import ClientSession

logger = logging.get_logger()


class FileLineProcessor:

    @staticmethod
    async def _process_lines(line_getter, process_f, logger_f, name):
        while True:
            try:
                line = await line_getter()
                if line != "":
                    await process_f(line)
                    logger_f(line)
                else:
                    break
            except ValueError:
                logger.error(
                    f"ValueError raised processing {name}, try with bigger "
                    "limiting size in config"
                )
        print(f"{Bcolors.WARNING}{name} sent empty data, {Bcolors.ENDC}")

    def __init__(self, name):
        self.name = name

    def log(self, line):
        raise NotImplementedError("Must be implemented")

    async def processing(self, line):
        raise NotImplementedError("Must be implemented")

    async def next_line(self):
        raise NotImplementedError("Must be implemented")

    async def process_f(self):
        return await FileLineProcessor._process_lines(
            self.next_line,
            self.processing,
            self.log,
            self.name
        )


class StdOutLineProcessor(FileLineProcessor):

    def __init__(self, process, session: ClientSession, execution_id: int,
                 api_ssl_enabled, api_kwargs):
        super().__init__("stdout")
        self.process = process
        self.execution_id = execution_id
        self.__session = session
        self.api_kwargs = api_kwargs
        self.api_ssl_enabled = api_ssl_enabled

    async def next_line(self):
        line = await self.process.stdout.readline()
        line = line.decode('utf-8')
        return line[:-1]

    def post_url(self):
        host = config.get('server', 'host')
        port = config.get('server', 'api_port')
        return api_url(
            host,
            port,
            postfix="/_api/v2/ws/"
                    f"{config.get('server', 'workspace')}/"
                    "bulk_create/",
            secure=self.api_ssl_enabled
        )

    async def processing(self, line):
        try:
            loaded_json = json.loads(line)
            print(f"{Bcolors.OKBLUE}{line}{Bcolors.ENDC}")
            headers = [
                (
                    "authorization",
                    f"agent {config.get('tokens', 'agent')}"
                )
            ]
            loaded_json["execution_id"] = self.execution_id

            res = await self.__session.post(
                self.post_url(),
                json=loaded_json,
                headers=headers,
                raise_for_status=False,
                ** self.api_kwargs
            )
            if res.status == 201:
                logger.info("Data sent to bulk create")
            else:
                logger.error(
                    "Invalid data supplied by the executor to the bulk create "
                    f"endpoint. Server responded: {res.status} "
                    f"{await res.text()}"
                    )

        except JSONDecodeError as e:
            logger.error("JSON Parsing error: {}".format(e))
            print(f"{Bcolors.WARNING}JSON Parsing error: {e}{Bcolors.ENDC}")

    def log(self, line):
        logger.debug(f"Output line: {line}")


class StdErrLineProcessor(FileLineProcessor):

    def __init__(self, process):
        super().__init__("stderr")
        self.process = process

    async def next_line(self):
        line = await self.process.stderr.readline()
        line = line.decode('utf-8')
        return line[:-1]

    async def processing(self, line):
        print(f"{Bcolors.FAIL}{line}{Bcolors.ENDC}")

    def log(self, line):
        logger.debug(f"Error line: {line}")
