from .core_parser import CoreParser
from pepys_import.core.formats import unit_registry
from pepys_import.core.formats.rep_line import REPLine


class NMEAParser(CoreParser):
    def __init__(self):
        super().__init__("NMEA File Format")

    def can_accept_suffix(self, suffix):
        return suffix.upper() == ".LOG" or suffix.upper() == ".TXT"

    def can_accept_filename(self, filename):
        return True

    def can_accept_first_line(self, first_line):
        return "$POSL" in first_line

    def can_process_file(self, file_contents):
        return True

    def process(self, data_store, path, file_contents, data_file_id):
        print("NMEA parser working on " + path)

        line_num = 0
        lat_tok = None
        lat_hem_tok = None
        long_tok = None
        long_hem_tok = None
        date_tok = None
        time_tok = None
        hdg_tok = None
        spd_tok = None

        ctr = 0

        for line_number, line in enumerate(file_contents):

            ctr += 1

            if ctr > 5000:
                break

            tokens = line.split(",")

            line_num += 1

            if len(tokens) > 0:

                msg_type = tokens[1]
                if msg_type == "DZA":
                    date_tok = tokens[2]
                    time_tok = tokens[3]
                elif msg_type == "VEL":
                    spd_tok = tokens[6]
                elif msg_type == "HDG":
                    hdg_tok = tokens[2]
                elif msg_type == "POS":
                    lat_tok = tokens[3]
                    lat_hem_tok = tokens[4]
                    long_tok = tokens[5]
                    long_hem_tok = tokens[6]

                # do we have all we need?
                if date_tok and spd_tok and hdg_tok and lat_tok:

                    # and finally store it
                    with data_store.session_scope():
                        datafile = data_store.search_datafile_by_id(data_file_id)
                        platform = data_store.add_to_platforms_from_rep(
                            "Toure", "Ferry", "FR", "Public"
                        )
                        sensor = data_store.add_to_sensors_from_rep(
                            platform.name + "_GPS", platform
                        )

                        state = REPLine(line_number + 1, line)

                        loc = self.parse_location(
                            lat_tok, lat_hem_tok, long_tok, long_hem_tok
                        )

                        state.set_location_obj(loc)
                        state.set_speed(
                            float(spd_tok) * unit_registry.metre / unit_registry.second
                        )
                        state.set_heading(float(hdg_tok) * unit_registry.degree)

                        data_store.add_state_to_states(
                            state, datafile, sensor,
                        )

                        date_tok = None
                        spd_tok = None
                        hdg_tok = None
                        lat_tok = None

    @staticmethod
    def parse_location(lat, lat_hem, lon, long_hem):
        lat_degrees = float(lat[0:2])
        lat_minutes = float(lat[2:4])
        lat_seconds = float(lat[4:])
        lat_degrees = lat_degrees + lat_minutes / 60 + lat_seconds / 60 / 60

        lon_degrees = float(lon[0:3])
        lon_minutes = float(lon[3:5])
        lon_seconds = float(lon[5:])
        lon_degrees = lon_degrees + lon_minutes / 60 + lon_seconds / 60 / 60

        if lat_hem == "S":
            lat_degrees = -1 * lat_degrees

        if lat_hem == "W":
            lon_degrees = -1 * lon_degrees

        return lat_degrees, lon_degrees
