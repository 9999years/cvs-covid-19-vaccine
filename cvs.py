from __future__ import annotations

from argparse import ArgumentParser
from dataclasses import dataclass, field
from enum import Enum
from types import TracebackType
from typing import Dict, Optional, ContextManager, Type, Any, List

import requests

BASE_URL = "https://www.cvs.com/immunizations/covid-19-vaccine"


@dataclass
class Session(ContextManager[requests.Session]):
    inner: requests.Session = field(default_factory=requests.Session)
    initialized: bool = False
    initialized_response: Optional[requests.Response] = None

    def ensure_init(self) -> Optional[requests.Response]:
        if self.initialized:
            return None
        else:
            self.initialized_response = self.inner.get(BASE_URL)
            self.initialized = True
            return self.initialized_response

    def __enter__(self) -> requests.Session:
        self.ensure_init()
        return self.inner

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> Optional[bool]:
        pass


class UsState(Enum):
    AL = "ALABAMA"
    AK = "ALASKA"
    AZ = "ARIZONA"
    AR = "ARKANSAS"
    CA = "CALIFORNIA"
    CO = "COLORADO"
    CT = "CONNECTICUT"
    DE = "DELAWARE"
    DC = "DISTRICT OF COLUMBIA"
    FL = "FLORIDA"
    GA = "GEORGIA"
    HI = "HAWAII"
    ID = "IDAHO"
    IL = "ILLINOIS"
    IN = "INDIANA"
    IA = "IOWA"
    KS = "KANSAS"
    KY = "KENTUCKY"
    LA = "LOUISIANA"
    ME = "MAINE"
    MD = "MARYLAND"
    MA = "MASSACHUSETTS"
    MI = "MICHIGAN"
    MN = "MINNESOTA"
    MS = "MISSISSIPPI"
    MO = "MISSOURI"
    MT = "MONTANA"
    NE = "NEBRASKA"
    NV = "NEVADA"
    NH = "NEW HAMPSHIRE"
    NJ = "NEW JERSEY"
    NM = "NEW MEXICO"
    NY = "NEW YORK"
    NC = "NORTH CAROLINA"
    ND = "NORTH DAKOTA"
    OH = "OHIO"
    OK = "OKLAHOMA"
    OR = "OREGON"
    PA = "PENNSYLVANIA"
    RI = "RHODE ISLAND"
    SC = "SOUTH CAROLINA"
    SD = "SOUTH DAKOTA"
    TN = "TENNESSEE"
    TX = "TEXAS"
    UT = "UTAH"
    VT = "VERMONT"
    VA = "VIRGINIA"
    WA = "WASHINGTON"
    WV = "WEST VIRGINIA"
    WI = "WISCONSIN"
    WY = "WYOMING"

    @classmethod
    def from_abbr(cls, abbr: str) -> Optional[UsState]:
        return cls.__members__.get(abbr, None)

    @property
    def url(self) -> str:
        return f"{BASE_URL}.vaccine-status.{self.name.lower()}.json?vaccineinfo"

    def get_info(self, session: Session):
        with session as session:
            return VaccineInfoResponse.from_json(
                session.get(self.url, headers={"Referer": BASE_URL}).json()
            )


@dataclass
class VaccineInfoResponse:
    payload: Optional[VaccineInfo] = None
    metadata: Dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_json(cls, obj: Dict[str, Any]) -> VaccineInfoResponse:
        return cls(
            payload=VaccineInfo.from_json(obj["responsePayloadData"]),
            metadata=obj["responseMetaData"],
        )


@dataclass
class VaccineInfo:
    current_time: str
    is_booking_completed: bool
    data: Dict[UsState, List[CvsStatus]]

    @classmethod
    def from_json(cls, obj: Dict[str, Any]) -> VaccineInfo:
        return cls(
            current_time=obj["currentTime"],
            is_booking_completed=obj["isBookingCompleted"],
            data={
                UsState.from_abbr(state): [
                    CvsStatus.from_json(pharmacy) for pharmacy in pharmacies
                ]
                for state, pharmacies in obj["data"].items()
            },
        )


class BookingStatus(Enum):
    full = "Fully Booked"
    available = "Available"


@dataclass
class CvsStatus:
    city: str
    state: UsState
    status: BookingStatus

    @classmethod
    def from_json(cls, obj: Dict[str, str]) -> CvsStatus:
        return cls(
            city=obj["city"],
            state=UsState.from_abbr(obj["state"]),
            status=BookingStatus(obj["status"]),
        )


def main() -> None:
    parser = ArgumentParser(
        description="""Find COVID-19 vaccine availabilities in a particular state"""
    )
    parser.add_argument(
        "state",
        type=UsState.get_abbr,
        help="""Two-letter US state code; e.g. MA, NH, WA...""",
    )
    args = parser.parse_args()

    sess = Session()
    state = args.state()
    data = state.get_info(sess)

    any_available = False
    cities = data.payload.data[state]

    for city in cities:
        if city.status != BookingStatus.full:
            print("Available:", city.city)
            any_available = True

    if not any_available:
        print(
            "No availabilities found; checked",
            len(cities),
            "CVS locations in",
            state.value.title(),
        )


if __name__ == "__main__":
    main()
