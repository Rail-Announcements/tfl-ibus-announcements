from operator import or_
from dotenv import load_dotenv
from linker import clean_name, DBSession, BusStop, BusRouteSection

load_dotenv()


def main():
    od_autocomplete = {}

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

    print("Linking origin/destinations")

    # Find audio files which are similar to the origin/destination names
    for section in bus_route_sections:
        if section.origin_audio_file is None:
            origin_name = clean_name(section.origin_name)

            if origin_name in od_autocomplete:
                section.origin_audio_file = od_autocomplete[origin_name]
                section.origin_audio_file_likeliness = 999
                continue

            filename = input(
                f"https://tfl.gov.uk/bus/route/{section.bus_route.id}?direction={section.direction} - Enter the filename for {origin_name}: "
            )

            if len(filename) > 0:
                od_autocomplete[origin_name] = filename
                section.origin_audio_file = filename
                section.origin_audio_file_likeliness = 999

        if section.destination_audio_file is None:
            destination_name = clean_name(section.destination_name)

            if destination_name in od_autocomplete:
                section.destination_audio_file = od_autocomplete[destination_name]
                section.destination_audio_file_likeliness = 999
                continue

            filename = input(
                f"https://tfl.gov.uk/bus/route/{section.bus_route.id}?direction={section.direction} - Enter the filename for {destination_name}: "
            )

            if len(filename) > 0:
                od_autocomplete[destination_name] = filename
                section.destination_audio_file = filename
                section.destination_audio_file_likeliness = 999

        DBSession.flush()
        DBSession.commit()
        DBSession.flush()

    s_autocomplete = {}
    print("Linking stops")

    for stop in bus_stops:
        n_id = stop.naptan_id
        # Remove last character from naptan_id if it's a letter
        if n_id[-1].isalpha():
            n_id = n_id[:-1]

        if stop.audio_file is None:
            stop_name = clean_name(stop.common_name)

            if n_id in s_autocomplete:
                stop.audio_file = s_autocomplete[n_id]
                stop.audio_file_likeliness = 999
                continue

            filename = input(
                f"https://tfl.gov.uk/bus/stop/{stop.naptan_id} - Enter the filename for {stop_name}: "
            )

            if len(filename) > 0:
                s_autocomplete[n_id] = filename
                stop.audio_file = filename
                stop.audio_file_likeliness = 999

        DBSession.flush()
        DBSession.commit()
        DBSession.flush()


if __name__ == "__main__":
    main()
