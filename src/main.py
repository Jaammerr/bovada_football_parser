import json
import random
import time
import pyuseragents

from pydantic import ValidationError
from loguru import logger
from tls_client import response as tls_response, Session as TLS_Session

from .errors import raise_for_status, TLSSessionError
from .models import *


logger.add("file.log", colorize=False, backtrace=True, diagnose=True)


class Parser(TLS_Session):
    """The use of the TLS client is intended to bypass possible blocking from parsing and partial demonstration of real browser requests"""

    def __init__(self, timeout: int, events_limit: int = 100, proxy: str = None):
        super().__init__()

        if proxy:
            self.setup_proxy(proxy)

        self.timeout: int = timeout
        self.events_limit: int = events_limit
        self.user_agent: str = pyuseragents.random()
        self.headers: dict = {
            "authority": "www.bovada.lv",
            "accept": "application/json, text/plain, */*",
            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "referer": "https://www.bovada.lv/",
            "user-agent": self.user_agent,
            "x-sport-context": "FOOT",
        }
        self.client_identifier: str = self.get_random_client_identifier()

    def setup_proxy(self, proxy: str) -> None:
        """Function for setting up proxy"""

        try:
            ip, port, user, password = proxy.split(":")
            proxy_str = f"http://{user}:{password}@{ip}:{port}"
            self.proxies: dict = {
                "http": proxy_str,
                "https": proxy_str,
            }

        except ValueError:
            raise TLSSessionError("Proxy must be in format ip:port:user:password")

    @staticmethod
    def get_random_client_identifier() -> str:
        """Function for getting random client identifier to fake the visibility of browser requests"""

        return random.choice(["Chrome110", "chrome111", "chrome112"])

    def get_football_events(
        self,
        url: str = "https://www.bovada.lv/services/sports/event/coupon/events/A/description/football",
    ) -> dict:
        """Function for getting main football events"""

        params = {
            "marketFilterId": "def",  # Default market filter
            "preMatchOnly": "true",  # If we set this parameter to false, we will get live events
            "eventsLimit": self.events_limit,  # Limit of events per request
            "lang": "en",  # Language
        }

        response: tls_response = self.get(
            url=url,
            params=params,
        )

        raise_for_status(response)
        return response.json()

    @staticmethod
    def validate_football_events(json_data: dict) -> list[FootballEventsList]:
        """Function for validating football events using pydantic models"""

        football_events = []
        for game in json_data:
            try:
                football_events.append(FootballEventsList.model_validate(game))
            except ValidationError as error:
                raise TLSSessionError(
                    f"Error while validating football events: {error}"
                )

        return football_events

    def get_additional_bets(
        self, events: list[FootballEventsList]
    ) -> list[FootballEventsList]:
        """Function for getting additional bets for each event in events list"""

        params = {
            "azSorting": "true",
            "lang": "en",
        }

        for event in events:
            for event_data in event.events:
                """Url for getting additional bets for each event"""
                url = f"https://www.bovada.lv/services/sports/event/coupon/events/A/description/{event_data.link}"

                response = self.get(url, params=params)
                raise_for_status(response)

                """If event has additional bets, we add them to additionalEvents list"""
                additionalEvents = (
                    event.additionalEvents if event.additionalEvents else []
                )

                for data in response.json():
                    try:
                        new_events_list = FootballEventsList.model_validate(data)
                        additionalEvents.extend(new_events_list.events)

                    except ValidationError as error:
                        logger.error(
                            f"Error while validating additional events: {error}"
                        )

                event.additionalEvents = additionalEvents

        return events

    @staticmethod
    def export_events_to_json(
        events: List[FootballEventsList], output_file: str
    ) -> None:
        """Function for exporting events to json file"""

        exported_data = []
        for event_list in events:
            """We need to combine events and additionalEvents lists into one list for more convenient work with data"""
            all_events = event_list.events + event_list.additionalEvents

            for event in all_events:
                event_info = {
                    "path": {
                        "id": event_list.path[0].id,
                        "link": event_list.path[0].link,
                        "description": event_list.path[0].description,
                        "type": event_list.path[0].type,
                        "sportCode": event_list.path[0].sportCode,
                    },
                    "id": event.id,
                    "link": event.link,
                    "sport": event.sport,
                    "startTime": event.startTime,
                    "live": event.live,
                    "competitors": [
                        {"_id": comp.id, "name": comp.name, "home": comp.home}
                        for comp in event.competitors
                    ],
                    "displayGroups": [
                        {
                            "id": group.id,
                            "description": group.description,
                            "markets": [
                                {
                                    "id": market.id,
                                    "description": market.description,
                                    "outcomes": [
                                        {
                                            "id": outcome.id,
                                            "description": outcome.description,
                                            "status": outcome.status,
                                            "type": outcome.type,
                                            "price": {
                                                "id": outcome.price.id,
                                                "handicap": outcome.price.handicap,
                                                "american": outcome.price.american,
                                                "decimal": outcome.price.decimal,
                                                "fractional": outcome.price.fractional,
                                                "malay": outcome.price.malay,
                                                "indonesian": outcome.price.indonesian,
                                                "hongkong": outcome.price.hongkong,
                                            },
                                        }
                                        for outcome in market.outcomes
                                    ],
                                }
                                for market in group.markets
                            ],
                        }
                        for group in event.displayGroups
                    ],
                }
                exported_data.append(event_info)

        with open(output_file, "w", encoding="utf-8") as json_file:
            json.dump(exported_data, json_file, ensure_ascii=False, indent=4)

    def run(self) -> None:
        while True:
            try:
                logger.info(f"Getting events..")
                events: dict = self.get_football_events()

                logger.info(f"Validating events..")
                events: list[FootballEventsList] = self.validate_football_events(events)

                logger.info(f"Getting additional bets for events..")
                events: list[FootballEventsList] = self.get_additional_bets(events)

                self.export_events_to_json(events, "../output.json")
                logger.info(f"Exported events to output.json")

                logger.debug(f"Sleeping for {self.timeout} seconds..\n")
                time.sleep(self.timeout)

            except (TLSSessionError, Exception) as error:
                logger.error(error)
                break
