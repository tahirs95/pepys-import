from .data_resolver import DataResolver


class DefaultResolver(DataResolver):
    # Hardcoded default values
    default_platform_name = "PLATFORM-1"
    default_platform_type = "Warship"
    default_nationality = "UK"
    default_sensor_name = "SENSOR-1"
    default_sensor_type = "Position"
    default_privacy = "PRIVACY-1"
    default_datafile_name = "DATAFILE-1"
    default_datafile_type = "DATAFILE-TYPE-1"

    def resolve_platform(
        self, data_store, platform_name, platform_type, nationality, privacy
    ):
        # needs to establish defaults for platform_name, platform_type, nationality and privacy
        if not platform_name:
            platform_name = self.default_platform_name

        if not platform_type:
            platform_type = data_store.search_platform_type(self.default_platform_type)
            if not platform_type:
                platform_type = data_store.add_to_platform_types(
                    self.default_platform_type
                )

        if not nationality:
            nationality = data_store.search_nationality(self.default_nationality)
            if not nationality:
                nationality = data_store.add_to_nationalities(self.default_nationality)

        if not privacy:
            privacy = data_store.search_privacy(self.default_privacy)
            if not privacy:
                privacy = data_store.add_to_privacies(self.default_privacy)

        return platform_name, platform_type, nationality, privacy

    def resolve_sensor(self, data_store, sensor_name, sensor_type, privacy):

        # needs to establish defaults for sensor name, sensor type, and privacy
        if not sensor_name:
            sensor_name = self.default_sensor_name

        if not sensor_type:
            default_sensor_type = data_store.search_sensor_type(
                self.default_sensor_type
            )
            if not default_sensor_type:
                sensor_type = data_store.add_to_sensor_types(self.default_sensor_type)

        if not privacy:
            privacy = self.resolve_privacy(data_store)

        return sensor_name, sensor_type, privacy

    def resolve_privacy(self, data_store):
        # needs to establish defaults for privacy
        privacy = data_store.search_privacy(self.default_privacy)
        if not privacy:
            privacy = data_store.add_to_privacies(self.default_privacy)

        return privacy

    def resolve_datafile(self, data_store, datafile_name, datafile_type, privacy):
        # needs to establish defaults for datafile name, datafile type, and privacy
        if not datafile_name:
            datafile_name = self.default_datafile_name

        datafile_type = data_store.search_datafile_type(self.default_datafile_type)
        if not datafile_type:
            datafile_type = data_store.add_to_datafile_types(self.default_datafile_type)

        privacy = data_store.search_privacy(self.default_privacy)
        if not privacy:
            privacy = data_store.add_to_privacies(self.default_privacy)

        return datafile_name, datafile_type, privacy
