from datetime import datetime
from .location import Location
from . import unit_registry
from pepys_import.utils.unit_utils import convert_absolute_angle, convert_speed
from pepys_import.file.highlighter.support.combine import combine_tokens


def parse_timestamp(date, time):
    if len(date) == 6:
        format_str = "%y%m%d"
    else:
        format_str = "%Y%m%d"

    if len(time) == 6:
        format_str += "%H%M%S"
    else:
        format_str += "%H%M%S.%f"

    return datetime.strptime(date + time, format_str)


class REPLine:
    def __init__(self, line_number, line, separator):
        self.importer_name = "Replay File Format Importer"

        self.line_num = line_number
        self.line = line
        self.separator = separator

        self.timestamp = None
        self.vessel = None
        self.symbology = None
        self.location = None
        self.heading = None
        self.speed = None
        self.depth = None
        self.text_label = None

        # Initialize pint's unit registry object
        self.unit_registry = unit_registry

    def print(self):
        print(
            "REP Line {} - Timestamp: {} Vessel: {} Symbology: {} Location: {} "
            "Heading: {} Speed: {} Depth: {} TextLabel: {}".format(
                self.line_num,
                self.timestamp,
                self.vessel,
                self.symbology,
                self.location,
                self.heading,
                self.speed,
                self.depth,
                self.text_label,
            )
        )

    def parse(self, errors, error_type):
        tokens = self.line.tokens()

        if len(tokens) < 15:
            errors.append(
                {
                    error_type: f"Error on line {self.line_num}. Not enough tokens: {self.line.text}"
                }
            )
            return False

        # separate token strings
        date_token = tokens[0]
        time_token = tokens[1]
        vessel_name_token = tokens[2]
        symbology_token = tokens[3]
        lat_degrees_token = tokens[4]
        lat_mins_token = tokens[5]
        lat_secs_token = tokens[6]
        lat_hemi_token = tokens[7]
        long_degrees_token = tokens[8]
        long_mins_token = tokens[9]
        long_secs_token = tokens[10]
        long_hemi_token = tokens[11]
        heading_token = tokens[12]
        speed_token = tokens[13]
        depth_token = tokens[14]

        if len(tokens) >= 16:
            self.text_label = " ".join([tok.text for tok in tokens[15:]])

        if len(date_token.text) != 6 and len(date_token.text) != 8:
            errors.append(
                {
                    error_type: f"Error on line {self.line_num}. Date format {date_token.text} "
                    f"should be either 2 of 4 figure date, followed by month then date"
                }
            )
            return False

        # Times always in Zulu/GMT
        if len(time_token.text) != 6 and len(time_token.text) != 10:
            errors.append(
                {
                    error_type: f"Line {self.line_num}. Error in Time format {time_token.text}. "
                    f"Should be HHMMSS[.SSS]"
                }
            )
            return False

        self.timestamp = parse_timestamp(date_token.text, time_token.text)
        combine_tokens(date_token, time_token).record(
            self.importer_name, "timestamp", self.timestamp, "n/a"
        )

        self.vessel = vessel_name_token.text.strip('"')
        vessel_name_token.record(self.importer_name, "vessel name", self.vessel, "n/a")

        symbology_values = symbology_token.text.split("[")
        if len(symbology_values) >= 1:
            if len(symbology_values[0]) != 2 and len(symbology_values[0]) != 5:
                errors.append(
                    {
                        error_type: f"Line {self.line_num}. Error in Symbology format "
                        f"{symbology_token.text}. Should be 2 or 5 chars"
                    }
                )
                return False
        if len(symbology_values) != 1 and len(symbology_values) != 2:
            errors.append(
                {
                    error_type: f"Line {self.line_num}. Error in Symbology format {symbology_token.text}"
                }
            )
            return False

        self.symbology = symbology_token.text

        self.location = Location(errors, error_type)
        if not self.location.set_latitude_dms(
            lat_degrees_token.text,
            lat_mins_token.text,
            lat_secs_token.text,
            lat_hemi_token.text,
        ):
            return False
        combine_tokens(
            lat_degrees_token, lat_mins_token, lat_secs_token, lat_hemi_token
        ).record(self.importer_name, "latitude", self.location, "DMS")

        if not self.location.set_longitude_dms(
            long_degrees_token.text,
            long_mins_token.text,
            long_secs_token.text,
            long_hemi_token.text,
        ):
            return False
        combine_tokens(
            long_degrees_token, long_mins_token, long_secs_token, long_hemi_token
        ).record(self.importer_name, "longitude", self.location, "DMS")

        heading = convert_absolute_angle(
            heading_token.text, self.line_num, errors, error_type
        )
        if not heading:
            return False

        self.heading = heading
        heading_token.record(self.importer_name, "heading", self.heading, "degrees")

        speed = convert_speed(
            speed_token.text, unit_registry.knots, self.line_num, errors, error_type
        )
        if not speed:
            return False
        self.speed = speed
        speed_token.record(self.importer_name, "speed", self.speed, "knots")

        try:
            if depth_token == "NaN":
                self.depth = 0.0
            else:
                self.depth = float(depth_token.text)
        except ValueError:
            errors.append(
                {
                    error_type: f"Line {self.line_num}. Error in depth value {depth_token.text}. "
                    f"Couldn't convert to a number"
                }
            )
            return False
        depth_token.record(self.importer_name, "depth", self.depth, "metres")

        return True

    def get_platform(self):
        return self.vessel

    def get_location(self):
        return self.location
