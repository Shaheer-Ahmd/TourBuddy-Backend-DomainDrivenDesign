from dataclasses import dataclass, field
from enum import Enum
from typing import List
@dataclass(frozen=True)
class SiteCategory(str, Enum):
    HISTORICAL = 1
    NATURAL_WONDER = 2
    CULTURAL_ATTRACTION = 3
    ADVENTURE_SPOT = 4

@dataclass(frozen = True)
class AccomodationCategory(str, Enum):
    LUXURY = 1
    BUDGET = 2
    MIDRANGE = 3

@dataclass
class Accomodation:
    id: str
    company: str
    category: AccomodationCategory
    cost: int


@dataclass(frozen=True)
class TransportationMode(str, Enum):
    CAR = 1
    TRAIN = 2
    AIRPLANE = 3

@dataclass
class Transportation:
    id: str
    company: str
    mode: TransportationMode
    cost: int

@dataclass(frozen=True)
class Location:
    latitude: float
    longitude: float

# @dataclass
# class Review:
#     rating: 
@dataclass
class Site:
    id: str
    name: str
    description: str
    category: SiteCategory
    location: str
    transportations: List[Transportation]=field(default_factory=list)
    accomodations: List[Accomodation]=field(default_factory=list)

    def add_transportation(self, tnsp: Transportation):
        self.transportations.append(tnsp)

    def add_accomodation(self, accm: Accomodation):
        self.accomodations.append(accm)