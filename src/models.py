from pydantic import BaseModel
from typing import List


class Competitors(BaseModel):
    id: str
    name: str
    home: bool


class Price(BaseModel):
    id: str
    handicap: str = None
    american: str
    decimal: str
    fractional: str
    malay: str
    indonesian: str
    hongkong: str


class OutComeData(BaseModel):
    id: str
    description: str
    status: str
    type: str
    price: Price


class MarketOutComes(BaseModel):
    id: str
    description: str
    outcomes: List[OutComeData]


class DisplayGroups(BaseModel):
    id: str
    description: str
    markets: List[MarketOutComes]


class FootballEvent(BaseModel):
    id: str
    link: str
    sport: str
    startTime: int
    live: bool
    competitors: List[Competitors]
    displayGroups: List[DisplayGroups]


class PathData(BaseModel):
    id: str
    link: str
    description: str
    type: str
    sportCode: str


class FootballEventsList(BaseModel):
    path: List[PathData]
    events: List[FootballEvent]
    additionalEvents: List[FootballEvent] = None
