import sys

from prompt_toolkit import prompt
from prompt_toolkit.completion import FuzzyWordCompleter
from sqlalchemy import or_

from pepys_import.resolvers.data_resolver import DataResolver
from pepys_import.resolvers.command_line_input import create_menu, is_valid
from pepys_import.core.store import constants


class CommandLineResolver(DataResolver):
    def __init__(self):
        super().__init__()

    def resolve_datafile(
        self, data_store, datafile_name, datafile_type, privacy, change_id
    ):
        choice = create_menu(
            f"Datafile '{datafile_name}' not found. Do you wish to: ",
            [
                f"Search for existing datafile",
                f"Add a new datafile, titled '{datafile_name}'",
            ],
            validate_method=is_valid,
        )

        if choice == str(1):
            return self.fuzzy_search_datafile(
                data_store, datafile_name, datafile_type, privacy, change_id
            )
        elif choice == str(2):
            return self.add_to_datafiles(
                data_store, datafile_name, datafile_type, privacy, change_id=change_id
            )
        elif choice == ".":
            print("Quitting")
            sys.exit(1)

    def resolve_platform(
        self, data_store, platform_name, platform_type, nationality, privacy, change_id
    ):
        choice = create_menu(
            f"Platform '{platform_name}' not found. Do you wish to: ",
            [
                f"Search for existing platform",
                f"Add a new platform, titled '{platform_name}'",
            ],
            validate_method=is_valid,
        )

        if choice == str(1):
            return self.fuzzy_search_platform(
                data_store,
                platform_name,
                platform_type,
                nationality,
                privacy,
                change_id,
            )
        elif choice == str(2):
            return self.add_to_platforms(
                data_store,
                platform_name,
                platform_type,
                nationality,
                privacy,
                change_id,
            )
        elif choice == ".":
            print("Quitting")
            sys.exit(1)

    def resolve_sensor(self, data_store, sensor_name, sensor_type, privacy, change_id):
        choice = create_menu(
            f"Sensor '{sensor_name}' not found. Do you wish to: ",
            [
                f"Search for existing sensor",
                f"Add a new sensor, titled '{sensor_name}'",
            ],
            validate_method=is_valid,
        )

        if choice == str(1):
            return self.fuzzy_search_sensor(
                data_store, sensor_name, sensor_type, privacy, change_id
            )
        elif choice == str(2):
            return self.add_to_sensors(
                data_store, sensor_name, sensor_type, privacy, change_id
            )
        elif choice == ".":
            print("Quitting")
            sys.exit(1)

    def resolve_privacy(self, data_store, change_id):
        # Choose Privacy
        privacy_names = [
            "Search an existing classification",
            "Add a new classification",
        ]
        choice = create_menu(
            f"Ok, please provide classification for new entry: ",
            privacy_names,
            validate_method=is_valid,
        )

        if choice == str(1):
            return self.fuzzy_search_privacy(data_store, change_id)
        elif choice == str(2):
            new_privacy = prompt("Please type name of new classification: ")
            privacy = data_store.search_privacy(new_privacy)
            if privacy:
                return privacy
            else:
                return data_store.add_to_privacies(new_privacy, change_id)
        elif choice == ".":
            print("-" * 61, "\nReturning to the previous menu\n")
            return None

    # Helper methods
    def fuzzy_search_datafile(
        self, data_store, datafile_name, datafile_type, privacy, change_id
    ):
        """
        This method parses all datafiles in the DB, and uses fuzzy search when
        user is typing. If user enters a new value, it adds to Synonym or Datafiles
        according to user's choice. If user selects an existing value, it returns the
        selected Datafile entity.

        :param data_store: A :class:`DataStore` object
        :type data_store: DataStore
        :param datafile_name:  Name of :class`Datafile`
        :type datafile_name: String
        :param datafile_type: Type of :class`Datafile`
        :type datafile_type: DatafileType
        :param privacy: Name of :class:`Privacy`
        :type privacy: Privacy
        :param change_id: ID of the :class:`Change` object
        :type change_id: Integer or UUID
        :return:
        """
        datafiles = data_store.session.query(data_store.db_classes.Datafile).all()
        completer = [datafile.reference for datafile in datafiles]
        choice = create_menu(
            "Please start typing to show suggested values",
            cancel="datafile search",
            choices=[],
            completer=FuzzyWordCompleter(completer),
        )
        if datafile_name and choice in completer:
            new_choice = create_menu(
                f"Do you wish to keep {datafile_name} as synonym for {choice}?",
                ["Yes", "No"],
            )
            if new_choice == str(1):
                datafile = (
                    data_store.session.query(data_store.db_classes.Datafile)
                    .filter(data_store.db_classes.Datafile.reference == choice)
                    .first()
                )
                # Add it to synonyms and return existing datafile
                data_store.add_to_synonyms(
                    constants.DATAFILE, datafile_name, datafile.datafile_id, change_id
                )
                print(f"'{datafile_name}' added to Synonyms!")
                return datafile
            elif new_choice == str(2):
                return self.add_to_datafiles(
                    data_store, datafile_name, datafile_type, privacy, change_id
                )
            elif new_choice == ".":
                print("-" * 61, "\nReturning to the previous menu\n")
                return self.fuzzy_search_datafile(
                    data_store, datafile_name, datafile_type, privacy, change_id
                )
        elif choice == ".":
            print("-" * 61, "\nReturning to the previous menu\n")
            return self.resolve_datafile(
                data_store, datafile_name, datafile_type, privacy, change_id
            )
        elif choice not in completer:
            print(f"'{choice}' could not found! Redirecting to adding a new datafile..")
            return self.add_to_datafiles(
                data_store, choice, datafile_type, privacy, change_id
            )

    def fuzzy_search_platform(
        self, data_store, platform_name, platform_type, nationality, privacy, change_id
    ):
        """
        This method parses all platforms in the DB, and uses fuzzy search when
        user is typing. If user enters a new value, it adds to Synonym or Platforms
        according to user's choice. If user selects an existing value, it returns the
        selected Platform entity.

        :param data_store: A :class:`DataStore` object
        :type data_store: DataStore
        :param platform_name: Name of :class:`Platform`
        :type platform_name: String
        :param nationality: Name of :class:`Nationality`
        :type nationality: Nationality
        :param platform_type: Name of :class:`PlatformType`
        :type platform_type: PlatformType
        :param privacy: Name of :class:`Privacy`
        :type privacy: Privacy
        :param change_id: ID of the :class:`Change` object
        :type change_id: Integer or UUID
        :return:
        """
        completer = list()
        platforms = data_store.session.query(data_store.db_classes.Platform).all()
        for platform in platforms:
            completer.append(platform.name)
            if platform.trigraph:
                completer.append(platform.trigraph)
            if platform.quadgraph:
                completer.append(platform.quadgraph)
        choice = create_menu(
            "Please start typing to show suggested values",
            cancel="platform search",
            choices=[],
            completer=FuzzyWordCompleter(completer),
        )
        if platform_name and choice in completer:
            new_choice = create_menu(
                f"Do you wish to keep {platform_name} as synonym for {choice}?",
                ["Yes", "No"],
                validate_method=is_valid,
            )
            if new_choice == str(1):
                platform = (
                    data_store.session.query(data_store.db_classes.Platform)
                    .filter(
                        or_(
                            data_store.db_classes.Platform.name == choice,
                            data_store.db_classes.Platform.trigraph == choice,
                            data_store.db_classes.Platform.quadgraph == choice,
                        )
                    )
                    .first()
                )
                # Add it to synonyms and return existing platform
                data_store.add_to_synonyms(
                    constants.PLATFORM, platform_name, platform.platform_id, change_id
                )
                print(f"'{platform_name}' added to Synonyms!")
                return platform
            elif new_choice == str(2):
                return self.add_to_platforms(
                    data_store,
                    platform_name,
                    platform_type,
                    nationality,
                    privacy,
                    change_id,
                )
            elif new_choice == ".":
                print("-" * 61, "\nReturning to the previous menu\n")
                return self.fuzzy_search_platform(
                    data_store,
                    platform_name,
                    platform_type,
                    nationality,
                    privacy,
                    change_id,
                )
        elif choice == ".":
            print("-" * 61, "\nReturning to the previous menu\n")
            return self.resolve_platform(
                data_store,
                platform_name,
                nationality,
                platform_type,
                privacy,
                change_id,
            )
        elif choice not in completer:
            print(f"'{choice}' could not found! Redirecting to adding a new platform..")
            return self.add_to_platforms(
                data_store, choice, platform_type, nationality, privacy, change_id
            )

    def fuzzy_search_sensor(
        self, data_store, sensor_name, sensor_type, privacy, change_id
    ):
        """
        This method parses all sensors in the DB, and uses fuzzy search when
        user is typing. If user enters a new value, it adds to Sensor table or searches
        for an existing sensor again. If user selects an existing value, it returns the
        selected Sensor entity.

        :param data_store: A :class:`DataStore` object
        :type data_store: DataStore
        :param sensor_name: Name of :class:`Sensor`
        :type sensor_name: Sensor
        :param sensor_type: Type of :class:`Sensor`
        :type sensor_type: SensorType
        :param privacy: Name of :class:`Privacy`
        :type privacy: Privacy
        :param change_id: ID of the :class:`Change` object
        :type change_id: Integer or UUID
        :return:
        """
        sensors = data_store.session.query(data_store.db_classes.Sensor).all()
        completer = [sensor.name for sensor in sensors]
        choice = create_menu(
            "Please start typing to show suggested values",
            cancel="sensor search",
            choices=[],
            completer=FuzzyWordCompleter(completer),
        )
        if sensor_name and choice in completer:
            new_choice = create_menu(
                f"Do you wish to keep {sensor_name} as synonym for {choice}?",
                ["Yes", "No"],
                validate_method=is_valid,
            )
            if new_choice == str(1):
                sensor = (
                    data_store.session.query(data_store.db_classes.Sensor)
                    .filter(data_store.db_classes.Sensor.name == choice)
                    .first()
                )
                # Add it to synonyms and return existing sensor
                data_store.add_to_synonyms(
                    constants.SENSOR, sensor_name, sensor.sensor_id, change_id
                )
                print(f"'{sensor_name}' added to Synonyms!")
                return sensor
            elif new_choice == str(2):
                return self.add_to_sensors(
                    data_store, sensor_name, sensor_type, privacy, change_id
                )
            elif new_choice == ".":
                print("-" * 61, "\nReturning to the previous menu\n")
                return self.fuzzy_search_sensor(
                    data_store, sensor_name, sensor_type, privacy, change_id
                )
        elif choice == ".":
            print("-" * 61, "\nReturning to the previous menu\n")
            return self.resolve_sensor(
                data_store, sensor_name, sensor_type, privacy, change_id
            )
        elif choice not in completer:
            print(f"'{choice}' could not found! Redirecting to adding a new sensor..")
            return self.add_to_sensors(
                data_store, sensor_name, sensor_type, privacy, change_id
            )

    def fuzzy_search_privacy(self, data_store, change_id):
        """
        This method parses all privacies in the DB, and uses fuzzy search when
        user is typing. If user enters a new value, it adds to Privacy table or searches
        for an existing privacy again. If user selects an existing value, it returns the
        selected Privacy entity.

        :param data_store: A :class:`DataStore` object
        :type data_store: DataStore
        :param change_id: ID of the :class:`Change` object
        :type change_id: Integer or UUID
        :return:
        """

        privacies = data_store.session.query(data_store.db_classes.Privacy).all()
        completer = [p.name for p in privacies]
        choice = create_menu(
            "Please start typing to show suggested values",
            cancel="classification search",
            choices=[],
            completer=FuzzyWordCompleter(completer),
        )
        if choice not in completer:
            new_choice = create_menu(
                f"You didn't select an existing classification. "
                f"Do you want to add '{choice}' ?",
                choices=["Yes", "No, I'd like to select an existing classification"],
                validate_method=is_valid,
            )
            if new_choice == str(1):
                return data_store.add_to_privacies(choice, change_id)
            elif new_choice == str(2):
                return self.fuzzy_search_privacy(data_store, change_id)
            elif new_choice == ".":
                print("-" * 61, "\nReturning to the previous menu\n")
                return self.resolve_privacy(data_store, change_id)
        else:
            return (
                data_store.session.query(data_store.db_classes.Privacy)
                .filter(data_store.db_classes.Privacy.name == choice)
                .first()
            )

    def fuzzy_search_datafile_type(self, data_store, datafile_name, change_id):
        """
        This method parses all datafile types in the DB, and uses fuzzy search when
        user is typing. If user enters a new value, it adds to DatafileType table or
        searches for an existing privacy again. If user selects an existing value,
        it returns the selected DatafileType entity.

        :param data_store: A :class:`DataStore` object
        :type data_store: DataStore
        :param datafile_name: Name of the Datafile
        :type datafile_name: String
        :param change_id: ID of the :class:`Change` object
        :type change_id: Integer or UUID
        :return:
        """

        datafile_types = data_store.session.query(
            data_store.db_classes.DatafileType
        ).all()
        completer = [p.name for p in datafile_types]
        choice = create_menu(
            "Please start typing to show suggested values",
            cancel="datafile type search",
            choices=[],
            completer=FuzzyWordCompleter(completer),
        )
        if choice == ".":
            print("-" * 61, "\nReturning to the previous menu\n")
            self.resolve_datafile_type(data_store, datafile_name, change_id)
        elif choice not in completer:
            new_choice = create_menu(
                f"You didn't select an existing datafile type. "
                f"Do you want to add '{choice}' ?",
                choices=["Yes", "No, I'd like to select an existing datafile type"],
                validate_method=is_valid,
            )
            if new_choice == str(1):
                return data_store.add_to_datafile_types(choice, change_id)
            elif new_choice == str(2):
                return self.fuzzy_search_datafile_type(
                    data_store, datafile_name, change_id
                )
            elif new_choice == ".":
                print("-" * 61, "\nReturning to the previous menu\n")
                return self.resolve_datafile_type(data_store, datafile_name, change_id)
        else:
            return (
                data_store.session.query(data_store.db_classes.DatafileType)
                .filter(data_store.db_classes.DatafileType.name == choice)
                .first()
            )

    def fuzzy_search_nationality(self, data_store, platform_name, change_id):
        """
        This method parses all Nationalities in the DB, and uses fuzzy search when
        user is typing. If user enters a new value, it adds to Nationality table or
        searches for an existing nationality again. If user selects an existing value,
        it returns the selected Nationality entity.

        :param platform_name:
        :param data_store: A :class:`DataStore` object
        :type data_store: DataStore
        :param change_id: ID of the :class:`Change` object
        :type change_id: Integer or UUID
        :return:
        """
        nationalities = data_store.session.query(
            data_store.db_classes.Nationality
        ).all()
        completer = [n.name for n in nationalities]
        choice = create_menu(
            "Please start typing to show suggested values",
            cancel="nationality search",
            choices=[],
            completer=FuzzyWordCompleter(completer),
        )
        if choice == ".":
            print("-" * 61, "\nReturning to the previous menu\n")
            return self.resolve_nationality(data_store, platform_name, change_id)
        elif choice not in completer:
            new_choice = create_menu(
                f"You didn't select an existing nationality. "
                f"Do you want to add '{choice}' ?",
                choices=["Yes", "No, I'd like to select an existing nationality"],
                validate_method=is_valid,
            )
            if new_choice == str(1):
                return data_store.add_to_nationalities(choice, change_id)
            elif new_choice == str(2):
                return self.fuzzy_search_nationality(
                    data_store, platform_name, change_id
                )
            elif new_choice == ".":
                print("-" * 61, "\nReturning to the previous menu\n")
                return self.resolve_nationality(data_store, platform_name, change_id)
        else:
            return (
                data_store.session.query(data_store.db_classes.Nationality)
                .filter(data_store.db_classes.Nationality.name == choice)
                .first()
            )

    def fuzzy_search_platform_type(self, data_store, platform_name, change_id):
        """
        This method parses all platform types in the DB, and uses fuzzy search when
        user is typing. If user enters a new value, it adds to PlatformType table or
        searches for an existing privacy again. If user selects an existing value,
        it returns the selected PlatformType entity.

        :param platform_name:
        :param data_store: A :class:`DataStore` object
        :type data_store: DataStore
        :param change_id: ID of the :class:`Change` object
        :type change_id: Integer or UUID
        :return:
        """
        platform_types = data_store.session.query(
            data_store.db_classes.PlatformType
        ).all()
        completer = [p.name for p in platform_types]
        choice = create_menu(
            "Please start typing to show suggested values",
            cancel="platform type search",
            choices=[],
            completer=FuzzyWordCompleter(completer),
        )
        if choice == ".":
            print("-" * 61, "\nReturning to the previous menu\n")
            self.resolve_platform_type(data_store, platform_name, change_id)
        elif choice not in completer:
            new_choice = create_menu(
                f"You didn't select an existing platform type. "
                f"Do you want to add '{choice}' ?",
                choices=["Yes", "No, I'd like to select an existing platform type"],
                validate_method=is_valid,
            )
            if new_choice == str(1):
                return data_store.add_to_platform_types(choice, change_id)
            elif new_choice == str(2):
                return self.fuzzy_search_platform_type(
                    data_store, platform_name, change_id
                )
            elif new_choice == ".":
                print("-" * 61, "\nReturning to the previous menu\n")
                return self.resolve_platform_type(data_store, platform_name, change_id)
        else:
            return (
                data_store.session.query(data_store.db_classes.PlatformType)
                .filter(data_store.db_classes.PlatformType.name == choice)
                .first()
            )

    def fuzzy_search_sensor_type(self, data_store, sensor_name, change_id):
        """
        This method parses all sensor types in the DB, and uses fuzzy search when
        user is typing. If user enters a new value, it adds to SensorType table or
        searches for an existing privacy again. If user selects an existing value,
        it returns the selected SensorType entity.

        :param sensor_name:
        :param data_store: A :class:`DataStore` object
        :type data_store: DataStore
        :param change_id: ID of the :class:`Change` object
        :type change_id: Integer or UUID
        :return:
        """
        sensor_types = data_store.session.query(data_store.db_classes.SensorType).all()
        completer = [sensor_type.name for sensor_type in sensor_types]
        choice = create_menu(
            "Please start typing to show suggested values",
            cancel="sensor type search",
            choices=[],
            completer=FuzzyWordCompleter(completer),
        )
        if choice == ".":
            print("-" * 61, "\nReturning to the previous menu\n")
            self.resolve_nationality(data_store, sensor_name, change_id)
        elif choice not in completer:
            new_choice = create_menu(
                f"You didn't select an existing sensor type. "
                f"Do you want to add '{choice}' ?",
                choices=["Yes", "No, I'd like to select a sensor type"],
                validate_method=is_valid,
            )
            if new_choice == str(1):
                return data_store.add_to_sensor_types(choice, change_id)
            elif new_choice == str(2):
                return self.fuzzy_search_sensor_type(data_store, sensor_name, change_id)
            elif new_choice == ".":
                print("-" * 61, "\nReturning to the previous menu\n")
                return self.resolve_sensor_type(data_store, sensor_name, change_id)
        else:
            return (
                data_store.session.query(data_store.db_classes.SensorType)
                .filter(data_store.db_classes.SensorType.name == choice)
                .first()
            )

    def resolve_nationality(self, data_store, platform_name, change_id):
        """
        This method asks user whether user wants to select from an existing nationality
        or add a new nationality. If user wants to select from an existing nationality,
        it returns the result from fuzzy search method. If user wants to add a new
        nationality, it searches DB first to prevent duplicates. If it is not found,
        it adds it to Nationality table. Finally, it returns the found or created entity

        :param platform_name:
        :param data_store: A :class:`DataStore` object
        :type data_store: DataStore
        :param change_id: ID of the :class:`Change` object
        :type change_id: Integer or UUID
        :return:
        """
        nationality_names = [
            "Search for an existing nationality",
            "Add a new nationality",
        ]
        choice = create_menu(
            "Please provide nationality: ", nationality_names, validate_method=is_valid
        )
        if choice == str(1):
            return self.fuzzy_search_nationality(data_store, platform_name, change_id)
        elif choice == str(2):
            new_nationality = prompt("Please type name of new nationality: ")
            return data_store.add_to_nationalities(new_nationality, change_id)
        elif choice == ".":
            print("-" * 61, "\nReturning to the previous menu\n")
            return None

    def resolve_platform_type(self, data_store, platform_name, change_id):
        platform_type_names = [
            "Search for an existing platform-type",
            "Add a new platform-type",
        ]
        choice = create_menu(
            "Ok, please provide platform-type: ",
            platform_type_names,
            validate_method=is_valid,
        )
        if choice == str(1):
            return self.fuzzy_search_platform_type(data_store, platform_name, change_id)
        elif choice == str(2):
            new_platform_type = prompt("Please type name of new platform-type: ")
            return data_store.add_to_platform_types(new_platform_type, change_id)
        elif choice == ".":
            print("-" * 61, "\nReturning to the previous menu\n")
            return None

    def resolve_sensor_type(self, data_store, sensor_name, change_id):
        """
        This method asks user whether user wants to select from an existing sensor type
        or add a new sensor type. If user wants to select from an existing sensor type,
        it returns the result from fuzzy search method. If user wants to add a new
        sensor type, it searches DB first to prevent duplicates. If it is not found,
        it adds it to SensorType table. Finally, it returns the found or created entity.

        :param sensor_name:
        :param data_store: A :class:`DataStore` object
        :type data_store: DataStore
        :param change_id: ID of the :class:`Change` object
        :type change_id: Integer or UUID
        :return:
        """
        sensor_type_names = [
            "Search for an existing sensor-type",
            "Add a new sensor-type",
        ]
        choice = create_menu(
            "Please provide sensor-type: ", sensor_type_names, validate_method=is_valid
        )

        if choice == str(1):
            return self.fuzzy_search_sensor_type(data_store, sensor_name, change_id)
        elif choice == str(2):
            new_input = prompt("Please type name of new sensor-type: ")
            return data_store.add_to_sensor_types(new_input, change_id)
        elif choice == ".":
            print("-" * 61, "\nReturning to the previous menu\n")
            return None

    def resolve_datafile_type(self, data_store, datafile_name, change_id):
        """

        :param data_store:
        :param datafile_name:
        :param change_id: ID of the :class:`Change` object
        :type change_id: Integer or UUID
        :return:
        """
        datafile_type_names = [
            "Search for an existing datafile-type",
            "Add a new datafile-type",
        ]
        choice = create_menu(
            "Ok, please provide datafile-type: ",
            datafile_type_names,
            validate_method=is_valid,
        )
        if choice == str(1):
            return self.fuzzy_search_datafile_type(data_store, datafile_name, change_id)
        elif choice == str(2):
            new_datafile_type = prompt("Please type name of new datafile-type: ")
            return data_store.add_to_datafile_types(new_datafile_type, change_id)
        elif choice == ".":
            print("-" * 61, "\nReturning to the previous menu\n")
            return None

    def add_to_datafiles(
        self, data_store, datafile_name, datafile_type, privacy, change_id
    ):
        """
        This method resolves datafile type and privacy. It asks user whether to create
        a datafile with resolved values or not. If user enters Yes, it returns all
        necessary data to create a datafile. If user enters No, it resolves values again

        :param data_store: A :class:`DataStore` object
        :type data_store: DataStore
        :param datafile_name:  Name of :class`Datafile`
        :type datafile_name: String
        :param datafile_type: Type of :class`Datafile`
        :type datafile_type: DatafileType
        :param privacy: Name of :class:`Privacy`
        :type privacy: Privacy
        :param change_id: ID of the :class:`Change` object
        :type change_id: Integer or UUID
        :return:
        """
        print("Ok, adding new datafile.")

        datafile_name = prompt("Please enter a name: ", default=datafile_name)
        # Choose Datafile Type
        if datafile_type:
            chosen_datafile_type = data_store.add_to_datafile_types(
                datafile_type, change_id
            )
        else:
            chosen_datafile_type = self.resolve_datafile_type(
                data_store, datafile_name, change_id
            )

        if chosen_datafile_type is None:
            return self.resolve_datafile(
                data_store, datafile_name, None, None, change_id
            )

        # Choose Privacy
        if privacy:
            chosen_privacy = data_store.add_to_privacies(privacy, change_id)
        else:
            chosen_privacy = self.resolve_privacy(data_store, change_id)

        if chosen_privacy is None:
            return self.resolve_datafile(
                data_store, datafile_name, None, None, change_id
            )

        print("-" * 61)
        print("Input complete. About to create this datafile:")
        print(f"Name: {datafile_name}")
        print(f"Type: {chosen_datafile_type.name}")
        print(f"Classification: {chosen_privacy.name}")

        choice = create_menu(
            "Create this datafile?: ",
            ["Yes", "No, make further edits"],
            validate_method=is_valid,
        )

        if choice == str(1):
            return datafile_name, chosen_datafile_type, chosen_privacy
        elif choice == str(2):
            return self.add_to_datafiles(
                data_store, datafile_name, None, None, change_id
            )
        elif choice == ".":
            print("-" * 61, "\nReturning to the previous menu\n")
            return self.resolve_datafile(
                data_store, datafile_name, None, None, change_id
            )

    def add_to_platforms(
        self, data_store, platform_name, platform_type, nationality, privacy, change_id
    ):
        """
        This method resolves platform type, nationality and privacy. It asks user
        whether to create a platform with resolved values or not. If user enters Yes,
        it returns all necessary data to create a platform.
        If user enters No, it resolves values again.

        :param data_store: A :class:`DataStore` object
        :type data_store: DataStore
        :param platform_name: Name of :class:`Platform`
        :type platform_name: String
        :param nationality: Name of :class:`Nationality`
        :type nationality: Nationality
        :param platform_type: Name of :class:`PlatformType`
        :type platform_type: PlatformType
        :param privacy: Name of :class:`Privacy`
        :type privacy: Privacy
        :param change_id: ID of the :class:`Change` object
        :type change_id: Integer or UUID
        :return:
        """
        print("Ok, adding new platform.")

        platform_name = prompt("Please enter a name: ", default=platform_name)
        trigraph = prompt(
            "Please enter trigraph (optional): ", default=platform_name[:3]
        )
        quadgraph = prompt(
            "Please enter quadgraph (optional): ", default=platform_name[:4]
        )
        pennant_number = prompt("Please enter pennant number (optional): ", default="")

        # Choose Nationality
        if nationality:
            chosen_nationality = data_store.add_to_nationalities(nationality, change_id)
        else:
            chosen_nationality = self.resolve_nationality(
                data_store, platform_name, change_id
            )

        if chosen_nationality is None:
            return self.resolve_platform(
                data_store, platform_name, None, None, None, change_id
            )

        # Choose Platform Type
        if platform_type:
            chosen_platform_type = data_store.add_to_platform_types(
                platform_type, change_id
            )
        else:
            chosen_platform_type = self.resolve_platform_type(
                data_store, platform_name, change_id
            )

        if chosen_platform_type is None:
            return self.resolve_platform(
                data_store, platform_name, None, None, None, change_id
            )

        # Choose Privacy
        if privacy:
            chosen_privacy = data_store.add_to_privacies(privacy, change_id)
        else:
            chosen_privacy = self.resolve_privacy(data_store, change_id)

        if chosen_privacy is None:
            return self.resolve_platform(
                data_store, platform_name, None, None, None, change_id
            )

        print("-" * 61)
        print("Input complete. About to create this platform:")
        print(f"Name: {platform_name}")
        print(f"Trigraph: {trigraph}")
        print(f"Quadgraph: {quadgraph}")
        print(f"Pennant Number: {pennant_number}")
        print(f"Nationality: {chosen_nationality.name}")
        print(f"Class: {chosen_platform_type.name}")
        print(f"Classification: {chosen_privacy.name}")

        choice = create_menu(
            "Create this platform?: ",
            ["Yes", "No, make further edits"],
            validate_method=is_valid,
        )

        if choice == str(1):
            return (
                platform_name,
                trigraph,
                quadgraph,
                pennant_number,
                chosen_platform_type,
                chosen_nationality,
                chosen_privacy,
            )
        elif choice == str(2):
            return self.add_to_platforms(
                data_store, platform_name, None, None, None, change_id
            )
        elif choice == ".":
            print("-" * 61, "\nReturning to the previous menu\n")
            return self.resolve_platform(
                data_store, platform_name, None, None, None, change_id
            )

    def add_to_sensors(self, data_store, sensor_name, sensor_type, privacy, change_id):
        """
        This method resolves sensor type and privacy. It returns existing or resolved
        sensor type and privacy entities.

        :param data_store: A :class:`DataStore` object
        :type data_store: DataStore
        :param sensor_name: Name of :class:`Sensor`
        :type sensor_name: Sensor
        :param sensor_type: Type of :class:`Sensor`
        :type sensor_type: SensorType
        :param privacy: Name of :class:`Privacy`
        :type privacy: Privacy
        :param change_id: ID of the :class:`Change` object
        :type change_id: Integer or UUID
        :return:
        """
        # Choose Sensor Type
        print("Ok, adding new sensor.")

        sensor_name = prompt("Please enter a name: ", default=sensor_name)
        if sensor_type:
            sensor_type = data_store.add_to_sensor_types(sensor_type, change_id)
        else:
            sensor_type = self.resolve_sensor_type(data_store, sensor_name, change_id)

        if sensor_type is None:
            return self.resolve_sensor(data_store, sensor_name, None, None, change_id)

        if privacy:
            privacy = data_store.add_to_privacies(privacy, change_id)
        else:
            privacy = self.resolve_privacy(data_store, change_id)

        if privacy is None:
            return self.resolve_sensor(data_store, sensor_name, None, None, change_id)

        print("-" * 61)
        print("Input complete. About to create this platform:")
        print(f"Name: {sensor_name}")
        print(f"Type: {sensor_type.name}")
        print(f"Classification: {privacy.name}")

        choice = create_menu(
            "Create this sensor?: ",
            ["Yes", "No, make further edits"],
            validate_method=is_valid,
        )

        if choice == str(1):
            return sensor_name, sensor_type, privacy
        elif choice == str(2):
            return self.add_to_sensors(data_store, sensor_name, None, None, change_id)
        elif choice == ".":
            print("-" * 61, "\nReturning to the previous menu\n")
            return self.resolve_sensor(data_store, sensor_name, None, None, change_id)
