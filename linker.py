from operator import or_
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
import re

from dotenv import load_dotenv

load_dotenv()

REQUIRED_MATCH_QUALITY = 91


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


def clean_name(name: str) -> str:
    name = f" {name} "
    name = name.replace(" Stn ", " Station ")
    name = name.replace(" St / ", " Street ")
    name = name.replace(" / ", " ")
    name = name.replace(" Coll ", " College ")
    name = name.replace(" Hosp ", " Hospital ")
    name = name.replace(" Rd ", " Road ")
    name = name.replace(" Grn ", " Green ")
    name = name.replace(" Pk ", " Park ")
    name = name.replace(" Cmn ", " Common ")
    name = name.replace(" Ln ", " Lane ")
    name = name.replace("'", "")
    name = name.replace(" Underground ", " ")
    name = name.replace(" DLR ", " ")
    name = name.replace(" R A F ", " RAF ")
    name = name.replace(" PH ", " Public House ")
    name = name.replace(" Rail Station ", " Station ")
    name = name.replace(" UR Church ", " United Reformed Church ")
    name = name.replace(" St. ", " St ")
    name = name.replace(" Y M C A ", " YMCA ")

    name = name.strip()

    if name.endswith(" St"):
        name = name[:-2] + "Street"

    if name.endswith(" Lan"):
        name = name[:-3] + "Lane"
        
    # Remove text in brackets
    name = re.sub(r"\(.*?\)", "", name)

    # Merge 2+ spaces
    name = " ".join(name.split())
    return name


all_stops = []
all_dests = []

# List filenames in ./Renamed/Stops
for root, dirs, files in os.walk("./Renamed/Stops"):
    for file in files:
        if file.endswith(".mp3"):
            all_stops.append(file[:-4])

# List filenames in ./Renamed/Destinations
for root, dirs, files in os.walk("./Renamed/Destinations"):
    for file in files:
        if file.endswith(".mp3"):
            all_dests.append(file[:-4])

from thefuzz import fuzz, process

# Get all bus stops
bus_stops = DBSession.query(BusStop).where(BusStop.audio_file.is_(None)).all()

# Get all bus route sections
bus_route_sections = (
    DBSession.query(BusRouteSection)
    .where(
        or_(
            BusRouteSection.origin_audio_file.is_(None),
            BusRouteSection.destination_audio_file.is_(None),
        )
    )
    .all()
)

# Find audio files which are similar to the origin/destination names
for section in bus_route_sections:
    origin_name = clean_name(section.origin_name)
    destination_name = clean_name(section.destination_name)

    origin_match = process.extractOne(
        origin_name,
        all_dests,
        scorer=fuzz.token_sort_ratio,
        score_cutoff=REQUIRED_MATCH_QUALITY,
    )
    if origin_match is None:
        origin_match = process.extractOne(
            origin_name,
            all_stops,
            scorer=fuzz.token_sort_ratio,
            score_cutoff=REQUIRED_MATCH_QUALITY,
        )

    destination_match = process.extractOne(
        destination_name,
        all_stops,
        scorer=fuzz.token_sort_ratio,
        score_cutoff=REQUIRED_MATCH_QUALITY,
    )
    if destination_match is None:
        destination_match = process.extractOne(
            destination_name,
            all_dests,
            scorer=fuzz.token_sort_ratio,
            score_cutoff=REQUIRED_MATCH_QUALITY,
        )

    if origin_match is not None:
        # print(f"Matched {origin_name}: {origin_match[0]}")
        section.origin_audio_file = origin_match[0]
        section.origin_audio_file_likeliness = origin_match[1]
    else:
        section.origin_audio_file = None
        section.origin_audio_file_likeliness = None
        print(f">>> No match for {origin_name} (sect id={section.id})")

    if destination_match is not None:
        # print(f"Matched {destination_name}: {destination_match[0]}")
        section.destination_audio_file = destination_match[0]
        section.destination_audio_file_likeliness = destination_match[1]
    else:
        section.destination_audio_file = None
        section.destination_audio_file_likeliness = None
        print(f">>> No match for {destination_name} (sect id={section.id})")

# Save models
DBSession.commit()

print("-----------------")

# Find audio files which are similar to the bus stop names
for stop in bus_stops:
    stop_name = clean_name(stop.common_name)

    # Merge 2+ spaces
    stop_name = " ".join(stop_name.split())

    match = process.extractOne(
        stop_name,
        all_stops,
        scorer=fuzz.token_sort_ratio,
        score_cutoff=REQUIRED_MATCH_QUALITY,
    )

    if match is not None:
        # print(f"Matched {stop_name}: {match[0]}")
        stop.audio_file = match[0]
        stop.audio_file_likeliness = match[1]
    else:
        stop.audio_file = None
        stop.audio_file_likeliness = None
        print(f">>> No match for {stop_name} (naptan id={stop.naptan_id})")


# Save models
DBSession.commit()
