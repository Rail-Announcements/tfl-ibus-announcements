import sys
import requests
import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    Column,
    ForeignKeyConstraint,
    Integer,
    Float,
    String,
    Table,
    Index,
    create_engine,
)
from sqlalchemy.orm import (
    scoped_session,
    sessionmaker,
    Mapped,
    relationship,
    DeclarativeBase,
)

from typing import Any, Dict
from dotenv import load_dotenv

load_dotenv()


# Open DB
class Base(DeclarativeBase):
    pass


DBSession = scoped_session(sessionmaker())
engine = create_engine("sqlite:///tfl.db", echo=False)

DBSession.remove()
DBSession.configure(bind=engine, autoflush=False, expire_on_commit=False)


class BusStop(Base):
    __table__ = Table(
        "bus_stops",
        Base.metadata,
        Column("naptan_id", String, primary_key=True),
        Column("indicator", String, nullable=True),
        Column("stop_letter", String, nullable=True),
        Column("stop_type", String, nullable=True),
        Column("common_name", String),
        Column("place_type", String),
        Column("lat", Float),
        Column("lon", Float),
        Column("compass_direction", String, nullable=True),
        Column("audio_file", String, nullable=True),
        Column("audio_file_likeliness", Integer, nullable=True, index=True),
        Index("ix_bus_stops_lat_lon", "lat", "lon"),
    )

    naptan_id: Mapped[str]
    indicator: Mapped[str]
    stop_letter: Mapped[str]
    stop_type: Mapped[str]
    common_name: Mapped[str]
    place_type: Mapped[str]
    lat: Mapped[float]
    lon: Mapped[float]
    compass_direction: Mapped[str]
    audio_file: Mapped[str | None]
    audio_file_likeliness: Mapped[float | None]

    def __repr__(self):
        return f"BusStop(naptan_id={self.naptan_id!r}, indicator={self.indicator!r}, stop_letter={self.stop_letter!r}, stop_type={self.stop_type!r}, common_name={self.common_name!r}, place_type={self.place_type!r}, lat={self.lat!r}, lon={self.lon!r}, compass_direction={self.compass_direction!r})"


class BusRoute(Base):
    __table__ = Table(
        "bus_routes",
        Base.metadata,
        Column("id", String, primary_key=True),
        Column("route_name", String),
    )

    id: Mapped[str]
    route_name: Mapped[str]

    route_sections = relationship("BusRouteSection", back_populates="bus_route")

    def __repr__(self):
        return f"BusRoute(id={self.id!r}, route_name={self.route_name!r})"


class BusRouteSection(Base):
    __table__ = Table(
        "bus_route_sections",
        Base.metadata,
        Column("id", String, primary_key=True),
        Column("route_id", String, index=True),
        Column("name", String),
        Column("direction", String),
        Column("origin_name", String),
        Column("origin_audio_file", String, nullable=True),
        Column("origin_audio_file_likeliness", Integer, nullable=True, index=True),
        Column("destination_name", String),
        Column("destination_audio_file", String, nullable=True),
        Column("destination_audio_file_likeliness", Integer, nullable=True, index=True),
        Column("origin_naptan_id", String, index=True),
        Column("destination_naptan_id", String, index=True),
        Column("line_strings", String),
        ForeignKeyConstraint(
            ["origin_naptan_id", "destination_naptan_id"],
            ["bus_stops.naptan_id", "bus_stops.naptan_id"],
        ),
        ForeignKeyConstraint(
            ["route_id"],
            ["bus_routes.id"],
        ),
    )

    id: Mapped[str]
    route_id: Mapped[str]
    name: Mapped[str]
    direction: Mapped[str]
    origin_name: Mapped[str]
    origin_audio_file: Mapped[str | None]
    origin_audio_file_likeliness: Mapped[float | None]
    destination_name: Mapped[str]
    destination_audio_file: Mapped[str | None]
    destination_audio_file_likeliness: Mapped[float | None]
    origin_naptan_id: Mapped[str]
    destination_naptan_id: Mapped[str]
    line_strings: Mapped[str]

    bus_route = relationship("BusRoute", back_populates="route_sections")
    stops = relationship("BusRouteSectionStops", back_populates="route_section")

    def __repr__(self):
        return f"BusRouteSection(id={self.id!r}, route_id={self.route_id!r}, name={self.name!r}, direction={self.direction!r}, origin_name={self.origin_name!r}, destination_name={self.destination_name!r}, origin_naptan_id={self.origin_naptan_id!r}, destination_naptan_id={self.destination_naptan_id!r}, line_strings={self.line_strings!r})"


class BusRouteSectionStops(Base):
    __table__ = Table(
        "bus_route_section_stops",
        Base.metadata,
        Column("id", Integer, primary_key=True, autoincrement=True),
        Column("route_section_id", String, index=True),
        Column("naptan_id", String, index=True),
        Column("sequence", Integer),
        ForeignKeyConstraint(["route_section_id"], ["bus_route_sections.id"]),
        ForeignKeyConstraint(["naptan_id"], ["bus_stops.naptan_id"]),
    )

    id: Mapped[int]
    route_section_id: Mapped[str]
    naptan_id: Mapped[str]
    sequence: Mapped[int]

    stop = relationship(
        "BusStop"
        # , back_populates="bus_route_section_stops"
    )
    route_section = relationship("BusRouteSection", back_populates="stops")

    def __repr__(self):
        return f"BusRouteSectionStops(id={self.id!r}, route_section_id={self.route_section_id!r}, naptan_id={self.naptan_id!r}, sequence={self.sequence!r})"


Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)


def get_stops_page(pageNumber: int) -> None | Dict[str, Any]:
    url = f"https://api.tfl.gov.uk/StopPoint/Mode/bus"

    app_id = os.getenv("TFL_APP_ID")
    app_key = os.getenv("TFL_APP_KEY")

    try:
        page = requests.get(
            url,
            params={"page": pageNumber, "app_id": app_id, "app_key": app_key},
            headers={
                "Accept": "application/json",
                "User-Agent": "https://github.com/davwheat",
            },
        ).json()
        return page
    except requests.exceptions.RequestException as e:
        print(e)
        return None


def get_routes() -> list[Dict[str, Any]]:
    url = f"https://api.tfl.gov.uk/Line/Route"

    app_id = os.getenv("TFL_APP_ID")
    app_key = os.getenv("TFL_APP_KEY")

    try:
        page = requests.get(
            url,
            params={
                "app_id": app_id,
                "app_key": app_key,
                "serviceTypes": "Regular,Night",
            },
            headers={
                "Accept": "application/json",
                "User-Agent": "https://github.com/davwheat",
            },
        ).json()

        # Filter to only bus routes
        return [x for x in page if x["modeName"] == "bus"]
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)


def get_route_info(route_id: str, direction: str) -> Dict[str, Any]:
    url = f"https://api.tfl.gov.uk/Line/{route_id}/Route/Sequence/{direction}"

    app_id = os.getenv("TFL_APP_ID")
    app_key = os.getenv("TFL_APP_KEY")

    try:
        page = requests.get(
            url,
            params={
                "app_id": app_id,
                "app_key": app_key,
                "serviceTypes": "Regular,Night",
                "excludeCrowding": "true",
            },
            headers={
                "Accept": "application/json",
                "User-Agent": "https://github.com/davwheat",
            },
        ).json()
        return page
    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)


def stops_to_class_objs(stopsArray: list[Any]) -> list[BusStop]:
    stops = []
    for stop in stopsArray:
        try:
            compass_dir = None

            # Extract compass direction from additional properties
            if "additionalProperties" in stop:
                for prop in stop["additionalProperties"]:
                    if prop["key"] == "CompassPoint":
                        compass_dir = prop["value"]
                        break

            stops.append(
                BusStop(
                    naptan_id=stop["naptanId"],
                    indicator=stop.get("indicator", None),
                    stop_letter=stop.get("stopLetter", None),
                    stop_type=stop.get("stopType", None),
                    common_name=stop["commonName"],
                    place_type=stop["placeType"],
                    lat=stop["lat"],
                    lon=stop["lon"],
                    compass_direction=compass_dir,
                )
            )

            # if "children" in stop and len(stop["children"]) > 0:
            #     stops += convertToClassObjs(stop["children"])

        except Exception as e:
            print(f"Error converting stop!")
            print(stop)
            print(e)
            sys.exit(1)

    return stops


def import_stops() -> None:
    pageNumber = 1
    stops_per_page = 1000

    while True:
        print(f"Getting page {pageNumber}...")
        stopsPage = get_stops_page(pageNumber)
        if stopsPage is None:
            break

        stops = stops_to_class_objs(stopsPage["stopPoints"])
        print(f"Adding {len(stops)} stops to DB...")

        # Check for duplicate naptan_ids
        naptan_ids = [stop.naptan_id for stop in stops]
        if len(naptan_ids) != len(set(naptan_ids)):
            print("Duplicate naptan_ids found!")

            # Print duplicates
            seen = set()
            duplicates = set(x for x in naptan_ids if x in seen or seen.add(x))

            print(duplicates)

            sys.exit(1)

        DBSession.add_all(stops)
        DBSession.commit()

        if pageNumber * stops_per_page >= stopsPage["total"]:
            print("Finished")
            break

        pageNumber += 1


def import_routes() -> None:
    routes = get_routes()

    for route in routes:
        # Add route
        DBSession.add(BusRoute(id=route["id"], route_name=route["name"]))

        for i, section in enumerate(route["routeSections"]):
            section_info = get_route_info(route["id"], section["direction"])
            section_id = f"{route['id']}_{section['direction']}_{i}"

            # Add route section
            DBSession.add(
                BusRouteSection(
                    id=section_id,
                    route_id=route["id"],
                    name=section["name"],
                    direction=section["direction"],
                    origin_name=section["originationName"],
                    destination_name=section["destinationName"],
                    origin_naptan_id=section["originator"],
                    destination_naptan_id=section["destination"],
                    line_strings=section_info["lineStrings"][
                        0
                    ],  # json.dumps(section_info["lineStrings"]),
                )
            )

            if len(section_info["orderedLineRoutes"]) > 1:
                print(
                    f"** Route {route['id']} ({section['name']}) has more than one route segment! We will ignore all but the first."
                )

            for lineRoutes in section_info["orderedLineRoutes"]:
                # Add route section stops
                for i, stop in enumerate(lineRoutes["naptanIds"]):
                    DBSession.add(
                        BusRouteSectionStops(
                            route_section_id=section_id,
                            naptan_id=stop,
                            sequence=i,
                        )
                    )

                # Ignore subsequent routes
                break

        print(f"Added route {route['id']}")
        DBSession.commit()


def main() -> None:
    import_stops()
    import_routes()


if __name__ == "__main__":
    main()
