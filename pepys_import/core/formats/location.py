from shapely import wkb


class Location:
    def __init__(self, errors=None, error_type=None):
        self._latitude = None
        self._longitude = None

        if errors is None:
            self.errors = list()
        else:
            self.errors = errors
        if error_type is None:
            self.error_type = "Location Parsing Error"
        else:
            self.error_type = error_type

    def __repr__(self):
        return f"Location(lon={self.longitude}, lat={self.latitude})"

    def __eq__(self, other):
        if not isinstance(other, Location):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.latitude == other.latitude and self.longitude == other.longitude

    # Property to make a read-only .latitude property
    # that mirrors the hidden _latitude attribute
    @property
    def latitude(self):
        return self._latitude

    @latitude.setter
    def latitude(self, value):
        raise AttributeError(
            "Cannot set latitude directly. Use set_latitude_decimal_degrees or set_latitude_dms"
        )

    # Property to make a read-only .longitude property
    # that mirrors the hidden _longitude attribute
    @property
    def longitude(self):
        return self._longitude

    @longitude.setter
    def longitude(self, value):
        raise AttributeError(
            "Cannot set longitude directly. Use set_longitude_decimal_degrees or set_longitude_dms"
        )

    def convert_and_check_degrees(self, degrees, lat_or_lon):
        try:
            degrees = float(degrees)
        except ValueError:
            self.errors.append(
                {
                    self.error_type: f"Error in {lat_or_lon} decimal degrees value {degrees}. Couldn't convert to a number"
                }
            )

            return None, False

        if lat_or_lon == "latitude":
            max_value = 90
            min_value = -90
        elif lat_or_lon == "longitude":
            max_value = 180
            min_value = -180
        if degrees < min_value or degrees > max_value:
            self.errors.append(
                {
                    self.error_type: f"Error in {lat_or_lon} degrees value {degrees}. Must be between 0 and 90"
                }
            )

            return None, False

        return degrees, True

    def convert_and_check_minutes(self, minutes, lat_or_lon):
        try:
            minutes = float(minutes)
        except ValueError:
            self.errors.append(
                {
                    self.error_type: f"Error in {lat_or_lon} minutes value {minutes}. Couldn't convert to a number"
                }
            )
            return None, False

        if minutes < 0 or minutes > 60:
            self.errors.append(
                {
                    self.error_type: f"Error in {lat_or_lon} minutes value {minutes}. Must be between 0 and 90"
                }
            )
            return None, False

        return minutes, True

    def convert_and_check_seconds(self, seconds, lat_or_lon):
        try:
            seconds = float(seconds)
        except ValueError:

            self.errors.append(
                {
                    self.error_type: f"Error in {lat_or_lon} seconds value {seconds}. Couldn't convert to a number"
                }
            )
            return None, False

        if seconds < 0 or seconds > 60:

            self.errors.append(
                {
                    self.error_type: f"Error in {lat_or_lon} seconds value {seconds}. Must be between 0 and 90"
                }
            )
            return None, False

        return seconds, True

    def convert_and_check_hemisphere(self, hemisphere, lat_or_lon):
        hemisphere = hemisphere.upper()

        if lat_or_lon == "latitude":
            valid_hemisphere_values = ("N", "S")
        elif lat_or_lon == "longitude":
            valid_hemisphere_values = ("E", "W")

        if hemisphere not in valid_hemisphere_values:
            self.errors.append(
                {
                    self.error_type: f"Error in {lat_or_lon} hemisphere value {hemisphere}. Must be {' or '.join(valid_hemisphere_values)}"
                }
            )
            return None, False

        return hemisphere, True

    def set_latitude_decimal_degrees(self, latitude):
        latitude, is_valid = self.convert_and_check_degrees(latitude, "latitude")

        if not is_valid:
            return False
        else:
            self._latitude = latitude
            return True

    def set_longitude_decimal_degrees(self, longitude):
        longitude, is_valid = self.convert_and_check_degrees(longitude, "longitude")

        if not is_valid:
            return False
        else:
            self._longitude = longitude
            return True

    def set_latitude_dms(self, degrees, minutes, seconds, hemisphere):
        degrees, is_valid = self.convert_and_check_degrees(degrees, "latitude")
        if not is_valid:
            return False

        minutes, is_valid = self.convert_and_check_minutes(minutes, "latitude")
        if not is_valid:
            return False

        seconds, is_valid = self.convert_and_check_seconds(seconds, "latitude")
        if not is_valid:
            return False

        hemisphere, is_valid = self.convert_and_check_hemisphere(hemisphere, "latitude")
        if not is_valid:
            return False

        decimal_degrees = degrees + (minutes / 60) + (seconds / 3600)

        if hemisphere == "S":
            decimal_degrees *= -1

        self._latitude = decimal_degrees
        return True

    def set_longitude_dms(self, degrees, minutes, seconds, hemisphere):
        degrees, is_valid = self.convert_and_check_degrees(degrees, "longitude")
        if not is_valid:
            return False

        minutes, is_valid = self.convert_and_check_minutes(minutes, "longitude")
        if not is_valid:
            return False

        seconds, is_valid = self.convert_and_check_minutes(seconds, "longitude")
        if not is_valid:
            return False

        hemisphere, is_valid = self.convert_and_check_hemisphere(
            hemisphere, "longitude"
        )
        if not is_valid:
            return False

        decimal_degrees = degrees + (minutes / 60) + (seconds / 3600)

        if hemisphere == "W":
            decimal_degrees *= -1

        self._longitude = decimal_degrees
        return True

    def to_wkt(self):
        return f"SRID=4326;POINT({self.longitude} {self.latitude})"

    def set_from_wkb(self, wkb_string):
        point = wkb.loads(wkb_string, hex=True)

        self._longitude = point.x
        self._latitude = point.y

    def set_from_wkt_string(self, wkt_string):
        longitude, latitude = wkt_string[16:-1].split()

        self._latitude = float(latitude)
        self._longitude = float(longitude)

    def check_valid(self):
        if self._latitude is None:
            return False

        if self._longitude is None:
            return False

        return True
