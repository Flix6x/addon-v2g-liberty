from datetime import datetime, timedelta
import pytz
import asyncio
import json
import os
import appdaemon.plugins.hass.hassapi as hass
import constants as c


class V2GLibertyGlobals(hass.Hass):
    # Entity to store entity (id's) that have been initialised,
    # so we know they should not be overwritten with the default setting_value.
    # This entity should never show up in the UI.
    # ha_initiated_entities_id: str = "input_text.initiated_ha_entities"
    v2g_settings: dict = {}
    settings_file_path = "/data/v2g_liberty_settings.json"
    v2g_main_app: object
    evse_client: object
    fm_client: object
    calendar_client: object

    SETTING_FM_ACCOUNT_USERNAME = {
        "entity_name": "fm_account_username",
        "entity_type": "input_text",
        "value_type": "str",
        "factory_default": None,
        "lister": None
    }
    SETTING_FM_ACCOUNT_PASSWORD = {
        "entity_name": "fm_account_password",
        "entity_type": "input_text",
        "value_type": "str",
        "factory_default": None,
        "lister": None
    }
    SETTING_FM_BASE_URL = {
        "entity_name": "fm_host_url",
        "entity_type": "input_text",
        "value_type": "str",
        "factory_default": "https://seita.energy",
        "lister": None
    }

    # Sensors for sending data to FM
    SETTING_FM_ACCOUNT_POWER_SENSOR_ID = {
        "entity_name": "fm_account_power_sensor_id",
        "entity_type": "input_number",
        "value_type": "int",
        "factory_default": 1,
        "lister": None
    }
    SETTING_FM_ACCOUNT_AVAILABILITY_SENSOR_ID = {
        "entity_name": "fm_account_availability_sensor_id",
        "entity_type": "input_number",
        "value_type": "int",
        "factory_default": 1,
        "lister": None
    }
    SETTING_FM_ACCOUNT_SOC_SENSOR_ID = {
        "entity_name": "fm_account_soc_sensor_id",
        "entity_type": "input_number",
        "value_type": "int",
        "lister": None
    }
    SETTING_FM_ACCOUNT_COST_SENSOR_ID = {
        "entity_name": "fm_account_cost_sensor_id",
        "entity_type": "input_number",
        "value_type": "int",
        "factory_default": 1,
        "lister": None
    }

    # Sensors for optimisation context in case of self_provided
    SETTING_FM_PRICE_PRODUCTION_SENSOR_ID = {
        "entity_name": "fm_own_price_production_sensor_id",
        "entity_type": "input_number",
        "value_type": "int",
        "factory_default": 1,
        "lister": None
    }
    SETTING_FM_PRICE_CONSUMPTION_SENSOR_ID = {
        "entity_name": "fm_own_price_consumption_sensor_id",
        "entity_type": "input_number",
        "value_type": "int",
        "factory_default": 1,
        "lister": None
    }
    SETTING_FM_EMISSIONS_SENSOR_ID = {
        "entity_name": "fm_own_emissions_sensor_id",
        "entity_type": "input_number",
        "value_type": "int",
        "factory_default": 1,
        "lister": None
    }
    SETTING_UTILITY_CONTEXT_DISPLAY_NAME = {
        "entity_name": "fm_own_context_display_name",
        "entity_type": "input_text",
        "value_type": "str",
        "factory_default": None,
        "lister": None
    }

    SETTING_OPTIMISATION_MODE = {
        "entity_name": "optimisation_mode",
        "entity_type": "input_select",
        "value_type": "str",
        "factory_default": "price",
        "lister": None
    }
    SETTING_ELECTRICITY_PROVIDER = {
        "entity_name": "electricity_provider",
        "entity_type": "input_select",
        "value_type": "str",
        "factory_default": "nl_generic",
        "lister": None
    }

    # Settings related to charger
    SETTING_CHARGER_HOST_URL = {
        "entity_name": "charger_host_url",
        "entity_type": "input_text",
        "value_type": "str",
        "factory_default": None,
        "lister": None
    }
    SETTING_CHARGER_PORT = {
        "entity_name": "charger_port",
        "entity_type": "input_number",
        "value_type": "int",
        "factory_default": 502,
        "lister": None
    }
    SETTING_CHARGER_PLUS_CAR_ROUNDTRIP_EFFICIENCY = {
        "entity_name": "charger_plus_car_roundtrip_efficiency",
        "entity_type": "input_number",
        "value_type": "int",
        "factory_default": 85,
        "lister": None
    }
    SETTING_CAR_MAX_CAPACITY_IN_KWH = {
        "entity_name": "car_max_capacity_in_kwh",
        "entity_type": "input_number",
        "value_type": "int",
        "factory_default": 24,
        "lister": None
    }
    SETTING_CAR_CONSUMPTION_WH_PER_KM = {
        "entity_name": "car_consumption_wh_per_km",
        "entity_type": "input_number",
        "value_type": "int",
        "factory_default": 175,
        "lister": None
    }

    SETTING_CAR_MIN_SOC_IN_PERCENT = {
        "entity_name": "car_min_soc_in_percent",
        "entity_type": "input_number",
        "value_type": "int",
        "factory_default": 20,
        "lister": None
    }
    SETTING_CAR_MAX_SOC_IN_PERCENT = {
        "entity_name": "car_max_soc_in_percent",
        "entity_type": "input_number",
        "value_type": "int",
        "factory_default": 80,
        "lister": None
    }
    SETTING_ALLOWED_DURATION_ABOVE_MAX_SOC_IN_HRS = {
        "entity_name": "allowed_duration_above_max_soc_in_hrs",
        "entity_type": "input_number",
        "value_type": "int",
        "factory_default": 12,
        "lister": None
    }

    SETTING_USE_REDUCED_MAX_CHARGE_POWER = {
        "entity_name": "use_reduced_max_charge_power",
        "entity_type": "input_boolean",
        "value_type": "bool",
        "factory_default": False,
        "lister": None
    }
    SETTING_CHARGER_MAX_CHARGE_POWER = {
        "entity_name": "charger_max_charging_power",
        "entity_type": "input_number",
        "value_type": "int",
        "factory_default": 1380,
        "min": 1380,
        "max": 25000,
        "lister": None
    }
    SETTING_CHARGER_MAX_DISCHARGE_POWER = {
        "entity_name": "charger_max_discharging_power",
        "entity_type": "input_number",
        "value_type": "int",
        "factory_default": 1380,
        "min": 1380,
        "max": 25000,
        "lister": None
    }

    # Settings related to showing prices
    SETTING_ENERGY_PRICE_VAT = {
        "entity_name": "energy_price_vat",
        "entity_type": "input_number",
        "value_type": "int",
        "factory_default": 0,
        "lister": None
    }
    SETTING_ENERGY_PRICE_MARKUP_PER_KWH = {
        "entity_name": "energy_price_markup_per_kwh",
        "entity_type": "input_number",
        "value_type": "float",
        "factory_default": 0,
        "lister": None
    }
    SETTING_ADMIN_MOBILE_NAME = {
        "entity_name": "admin_mobile_name",
        "entity_type": "input_select",
        "value_type": "str",
        "factory_default": None,
        "lister": None
    }
    SETTING_ADMIN_MOBILE_PLATFORM = {
        "entity_name": "admin_mobile_platform",
        "entity_type": "input_select",
        "value_type": "str",
        "factory_default": "ios",
        "lister": None
    }

    SETTING_CAR_CALENDAR_SOURCE = {
        "entity_name": "car_calendar_source",
        "entity_type": "input_select",
        "value_type": "str",
        "factory_default": "Direct caldav source",
        "lister": None
    }
    SETTING_INTEGRATION_CALENDAR_ENTITY_NAME = {
        "entity_name": "integration_calendar_entity_name",
        "entity_type": "input_select",
        "value_type": "str",
        "factory_default": "",
        "lister": None
    }

    SETTING_CALENDAR_ACCOUNT_INIT_URL = {
        "entity_name": "calendar_account_init_url",
        "entity_type": "input_text",
        "value_type": "str",
        "factory_default": None,
        "lister": None
    }
    SETTING_CALENDAR_ACCOUNT_USERNAME = {
        "entity_name": "calendar_account_username",
        "entity_type": "input_text",
        "value_type": "str",
        "factory_default": None,
        "lister": None
    }
    SETTING_CALENDAR_ACCOUNT_PASSWORD = {
        "entity_name": "calendar_account_password",
        "entity_type": "input_text",
        "value_type": "str",
        "factory_default": None,
        "lister": None
    }
    SETTING_CAR_CALENDAR_NAME = {
        "entity_name": "car_calendar_name",
        "entity_type": "input_select",
        "value_type": "str",
        "factory_default": None,
        "lister": None
    }

    # Used by method __collect_action_triggers
    collect_action_handle = None

    async def initialize(self):
        self.log("Initializing V2GLibertyGlobals")
        c.TZ = pytz.timezone(self.get_timezone())

        self.v2g_main_app = await self.get_app("v2g_liberty")
        self.evse_client = await self.get_app("modbus_evse_client")
        self.fm_client = await self.get_app("flexmeasures-client")
        self.calendar_client = await self.get_app("reservations-client")

        await self.__retrieve_settings()
        await self.__initialise_devices()
        await self.__read_and_process_charger_settings()
        await self.__read_and_process_calendar_client_settings()
        await self.__read_and_process_fm_client_settings()
        await self.__read_and_process_general_settings()
        # Has to run after __read_and_process_calendar_client_settings()
        await self.__init_car_calendar()

        self.listen_event(self.__test_charger_connection, "TEST_CHARGER_CONNECTION")
        self.listen_event(self.__init_car_calendar, "TEST_CALENDAR_CONNECTION")

        # Was None, which blocks processing during initialisation
        self.collect_action_handle = ""
        self.log("Completed initializing V2GLibertyGlobals")

    async def __init_car_calendar(self, event=None, data=None, kwargs=None):
        # Get the possible calendars from the validated account
        # if 0 set persistent notification
        # if current one is not in list set persistent notification
        # Populate the input_select XX with possible calendars from the validated account
        # Select the right option
        # Add a listener
        self.log("__init_car_calendar called")
        await self.set_state("input_text.calendar_account_connection_status", state="Trying to connect...")
        # reset options in calendar_name select
        calendar_names = []
        self.call_service("input_select/set_options", entity_id="input_select.car_calendar_name",
                          options=calendar_names)

        res = await self.calendar_client.initialise_calendar()
        self.log(f"__init_car_calendar called, res: {res}.")
        if res != "success":
            await self.set_state("input_text.calendar_account_connection_status", state=res)
            return

        # A conditional card in the dashboard is dependent on exactly the text "Successfully connected".
        await self.set_state("input_text.calendar_account_connection_status", state="Successfully connected")
        calendar_names = await self.calendar_client.get_calendar_names()
        self.log(f"__init_car_calendar called, calendar_names: {calendar_names}.")
        if len(calendar_names) == 0:
            # TODO: Also show this directly in UI, not only in
            message = f"No calendars available on {c.CALENDAR_ACCOUNT_INIT_URL} " \
                      f"A car reservation calendar is essential for V2G Liberty. " \
                      f"Please arrange for one.<br/>"
            self.log(f"Configuration error: {message}.")
            # TODO: Research if showing this only to admin users is possible.
            await self.call_service('persistent_notification/create', title="Configuration error", message=message,
                                    notification_id="notification_config_error")
            calendar_names = ["No calenders found"]

        if c.CAR_CALENDAR_SOURCE == "Direct caldav source":
            self.call_service("input_select/set_options", entity_id="input_select.car_calendar_name",
                              options=calendar_names)
            # TODO: If no stored_setting is found:
            # try guess a good default by selecting the first option that has "car" or "auto" in it's name.
            c.CAR_CALENDAR_NAME = await self.__process_setting(
                setting_object=self.SETTING_CAR_CALENDAR_NAME,
                callback=self.__read_and_process_calendar_client_settings
            )
            await self.calendar_client.activate_selected_calendar()
        else:
            self.call_service("input_select/set_options", entity_id="input_select.integration_calendar_entity_name",
                              options=calendar_names)
            c.INTEGRATION_CALENDAR_ENTITY_NAME = await self.__process_setting(
                setting_object=self.SETTING_INTEGRATION_CALENDAR_ENTITY_NAME,
                callback=self.__read_and_process_calendar_client_settings
            )

        self.log("Completed __init_car_calendar")

    async def __initialise_devices(self):
        # List of all the recipients to notify
        # Check if Admin is configured correctly
        # Warn user about bad config with persistent notification in UI.
        self.log("Initializing devices configuration")

        c.NOTIFICATION_RECIPIENTS.clear()
        # Service "mobile_app_" seems more reliable than using get_trackers,
        # as these names do not always match with the service.
        for service in self.list_services():
            if service["service"].startswith("mobile_app_"):
                c.NOTIFICATION_RECIPIENTS.append(service["service"].replace("mobile_app_", ""))
                # TODO?? Get current selected option and set it again after populating

        if len(c.NOTIFICATION_RECIPIENTS) == 0:
            message = f"No mobile devices (e.g. phone, tablet, etc.) have been registered in Home Assistant " \
                      f"for notifications.<br/>" \
                      f"It is highly recommended to do so. Please install the HA companion app on your mobile device " \
                      f"and connect it to Home Assistant.<br/>"
            self.log(f"Configuration error: {message}.")
            # TODO: Research if showing this only to admin users is possible.
            await self.call_service('persistent_notification/create', title="Configuration error", message=message,
                                    notification_id="notification_config_error")
        else:
            self.log(f"__initialise_devices - recipients for notifications: {c.NOTIFICATION_RECIPIENTS}.")
            self.call_service("input_select/set_options", entity_id="input_select.admin_mobile_name",
                              options=c.NOTIFICATION_RECIPIENTS)

        self.log("Completed Initializing devices configuration")

    async def __test_charger_connection(self, event, data, kwargs):
        """ Tests the connection with the charger and processes the maximum charge power read from the charger
            Called from the settings page."""
        self.log("__test_charger_connection called")
        # The url and port settings have been changed via the listener
        await self.set_state("input_text.charger_connection_status", state="Trying to connect...")
        if not await self.evse_client.initialise_charger():
            await self.set_state("input_text.charger_connection_status", state="Failed to connect")
            return
        # min/max power is set self.evse_client.initialise_charger()
        # A conditional card in the dashboard is dependent on exactly the text "Successfully connected".
        await self.set_state("input_text.charger_connection_status", state="Successfully connected")

    async def __retrieve_settings(self):
        """Retrieve all settings from the settings file
        """
        self.log(f"__retrieve_settings called")

        str_dict = ""
        if not os.path.exists(self.settings_file_path):
            self.log(f"__retrieve_settings, create settings file")
            with open(self.settings_file_path, 'w') as file:
                file.write(" ")
        else:
            with open(self.settings_file_path, 'r') as file:
                str_dict = json.load(file)
            self.log(f"__retrieve_settings, str_list: {str_dict}")
        if str_dict is None or str_dict == "":
            self.v2g_settings = {}
        else:
            self.v2g_settings = json.loads(str_dict)

        self.log(f"__retrieve_settings, self.v2g_settings: {self.v2g_settings}")

    async def __store_setting(self, entity_id: str, setting_value: any):
        """Store (overwrite or create) a setting in settings file.

        Args:
            entity_id (str): setting name = the full entity_id from HA
            setting_value: the value to set.
        """
        # self.log(f"__store_setting, entity_id: {entity_id}")
        self.v2g_settings[entity_id] = setting_value
        str_dict = json.dumps(self.v2g_settings)
        # self.log(f"__store_setting, to write str_dict: {str_dict}")
        # if not os.path.exists(self.settings_file_path):
        #     self.log(f"__store_setting, create settings file")
        # else:
        #     self.log(f"__store_setting, overwriting settings file")
        with open(self.settings_file_path, 'w') as write_file:
            json.dump(str_dict, write_file)

    async def __write_setting_to_ha(self, setting: dict, setting_value, min_allowed_value=None, max_allowed_value=None):
        """
           This method writes the value to the HA entity.
        """
        entity_name = setting['entity_name']
        entity_type = setting['entity_type']
        entity_id = f"{entity_type}.{entity_name}"
        self.log(f'__write_setting_to_ha called with value {setting_value} for entity {entity_id}.')

        if setting_value is not None:
            # setting_value has a relevant setting_value to set to HA
            if entity_type == "input_select":
                await self.select_option(entity_id, setting_value)
            elif entity_type == "input_boolean":
                if setting_value is True:
                    await self.turn_on(entity_id)
                else:
                    await self.turn_off(entity_id)
            else:
                # Unfortunately the UI does not pickup these new limits... from the attributes, so need to check locally.
                # new_attributes = {}
                # if min_allowed_value:
                #     new_attributes["min"] = min_allowed_value
                # if max_allowed_value:
                #     new_attributes["max"] = max_allowed_value

                # self.log(f"__write_setting() attributes-to-write: {new_attributes}.")

                # # Assume input_text or input_number
                # if new_attributes:
                #     await self.set_state(entity_id, state=setting_value, attributes=new_attributes)
                # else:
                await self.set_state(entity_id, state=setting_value)

    async def __process_setting(self, setting_object: dict, callback):
        """
           This method checks if the setting-entity is empty, if so:
           - set the setting-entity setting_value to the default that is set in constants
           if not empty:
           - return the setting_value of the setting-entity
        """
        if setting_object == self.SETTING_CAR_CALENDAR_NAME:
            self.log("self.SETTING_CAR_CALENDAR_NAME. Callback: {callback}")

        entity_name = setting_object['entity_name']
        entity_type = setting_object['entity_type']
        entity_id = f"{entity_type}.{entity_name}"
        setting_entity = await self.get_state(entity_id, attribute="all")

        # Get the setting from store
        stored_setting_value = self.v2g_settings.get(entity_id, None)

        # At first initial run the listener is filled with a callback handler.
        if setting_object['lister'] is None:
            # read the setting from store, write to UI and return it so the constant can be set.
            return_value = ""
            if stored_setting_value is None:
                # v2g_setting was empty, populate it with the factory default from settings_object
                factory_default = setting_object['factory_default']
                if factory_default is not None and factory_default != "":
                    return_value, has_changed = self.__check_and_convert_value(setting_object, factory_default)
                    self.log(f"__process_setting, Initial call. No relevant v2g_setting. "
                             f"Set constant and UI to factory_default: {return_value} {type(return_value)}.")
                    await self.__store_setting(entity_id=entity_id, setting_value=return_value)
                    await self.__write_setting_to_ha(setting=setting_object, setting_value=return_value)
                elif entity_type == "input_select":
                    # If no value is set on an input_select, the first option automatically gets selected;
                    # store this setting, but not if it is empty or "Please choose an option".
                    return_value = setting_entity.get('state', None)
                    if return_value is not None and return_value not in ["", "unknown", "Please choose an option"]:
                        await self.__store_setting(entity_id=entity_id, setting_value=return_value)
                else:
                    # There is no relevant default to set..
                    self.log("__process_setting: setting '{entity_id}' has no value in store yet but also no relevant "
                             "default to set it to.")
                    pass
            else:
                # Initial call with relevant v2g_setting.
                # Write that to HA for UI and return this value to set in constants
                return_value, has_changed = self.__check_and_convert_value(setting_object, stored_setting_value)
                self.log(f"__process_setting, Initial call. Relevant v2g_setting: {return_value}, "
                         f"write this to HA entity '{entity_id}'.")
                await self.__write_setting_to_ha(setting=setting_object, setting_value=return_value)

            if callback is not None:
                setting_object['lister'] = self.listen_state(callback, entity_id, attribute="all")

        else:
            # Not the initial call, so this is triggered by changed value in UI
            # Write value from HA to store and constant
            state = setting_entity.get('state', None)
            return_value, has_changed = self.__check_and_convert_value(setting_object, state)
            self.log(f"__process_setting. Triggered by changes in UI. "
                     f"Write value '{return_value}' to store '{entity_id}'.")
            if has_changed:
                await self.__write_setting_to_ha(setting=setting_object, setting_value=return_value)
            await self.__store_setting(entity_id=entity_id, setting_value=return_value)

        # Just for logging
        # Not an exact match of the constant name but good enough for logging
        message = f"v2g_globals, __process_setting set c.{entity_name.upper()} to "
        mode = setting_entity["attributes"].get("mode", 'none').lower()
        if mode == "password":
            message = f"{message} ********"
        else:
            message = f"{message} {return_value}"

        uom = setting_entity['attributes'].get('unit_of_measurement')
        if uom:
            message = f"{message} {uom}."
        else:
            message = f"{message}."
        self.log(message)

        return return_value

    def __check_and_convert_value(self, setting_object, value_to_convert):
        """ Check number against min/max from setting object, altering to stay within these limits.
            Convert to required type (in setting object)

        Args:
            setting_object (dict): dict with setting_object with entity_type/name and min/max
            number_to_check (_type_): the number to check

        Returns:
            any: depending on the setting type
        """
        entity_id = f"{setting_object['entity_type']}.{setting_object['entity_name']}"
        value_type = setting_object.get('value_type', "str")
        has_changed = False
        min_value = setting_object.get('min', None)
        max_value = setting_object.get('max', None)
        if value_type == "float":
            return_value = float(value_to_convert)
            rv = return_value
            if min_value:
                min_value = float(min_value)
                rv = max(min_value, return_value)
            if max_value:
                max_value = float(max_value)
                rv = min(max_value, return_value)
            if rv != return_value:
                has_changed = True
                return_value = rv
        elif value_type == "int":
            # Assume int
            return_value = int(float(value_to_convert))
            rv = return_value
            if min_value:
                min_value = int(float(min_value))
                rv = max(min_value, return_value)
            if max_value:
                max_value = int(float(max_value))
                rv = min(max_value, return_value)
            if rv != return_value:
                has_changed = True
                return_value = rv
        elif value_type == "bool":
            if value_to_convert or value_to_convert in ['true', 'True', 'on']:
                return_value = True
            else:
                return_value = False
        elif value_type == "str":
            return_value = str(value_to_convert)

        if has_changed:
            msg = f"Adjusted '{entity_id}' to '{return_value}' to stay within limits."
            ntf_id = f"auto_adjusted_setting_{entity_id}"
            self.create_persistent_notification(message=msg, title='Automatically adjusted setting',
                                                notification_id=ntf_id)
            self.log(f"__check_and_convert_number {msg}")
        return return_value, has_changed

    async def __cancel_listening(self, setting: dict):
        if setting['lister'] is None:
            return
        else:
            await self.cancel_listen_state(setting['lister'])
            setting['lister'] = None

    async def __read_and_process_charger_settings(self, entity=None, attribute=None, old=None, new=None, kwargs=None):

        callback_method = self.__read_and_process_charger_settings

        c.CHARGER_HOST_URL = await self.__process_setting(
            setting_object=self.SETTING_CHARGER_HOST_URL,
            callback=callback_method
        )
        c.CHARGER_PORT = await self.__process_setting(
            setting_object=self.SETTING_CHARGER_PORT,
            callback=callback_method
        )
        c.CHARGER_PLUS_CAR_ROUNDTRIP_EFFICIENCY = await self.__process_setting(
            setting_object=self.SETTING_CHARGER_PLUS_CAR_ROUNDTRIP_EFFICIENCY,
            callback=callback_method
        )
        c.ROUNDTRIP_EFFICIENCY_FACTOR = c.CHARGER_PLUS_CAR_ROUNDTRIP_EFFICIENCY / 100

        use_reduced_max_charge_power = False
        use_reduced_max_charge_power = await self.__process_setting(
            setting_object=self.SETTING_USE_REDUCED_MAX_CHARGE_POWER,
            callback=callback_method
        )
        if use_reduced_max_charge_power:
            # set c.CHARGER_MAX_CHARGE_POWER and c.CHARGER_MAX_DISCHARGE_POWER to max from settings page
            c.CHARGER_MAX_CHARGE_POWER = await self.__process_setting(
                setting_object=self.SETTING_CHARGER_MAX_CHARGE_POWER,
                callback=callback_method
            )
            c.CHARGER_MAX_DISCHARGE_POWER = await self.__process_setting(
                setting_object=self.SETTING_CHARGER_MAX_DISCHARGE_POWER,
                callback=callback_method
            )
        else:
            # set c.CHARGER_MAX_CHARGE_POWER and c.CHARGER_MAX_DISCHARGE_POWER to max from charger
            # cancel callbacks for SETTINGS.
            await self.__cancel_listening(self.SETTING_CHARGER_MAX_CHARGE_POWER)
            await self.__cancel_listening(self.SETTING_CHARGER_MAX_DISCHARGE_POWER)
            c.CHARGER_MAX_CHARGE_POWER = self.SETTING_CHARGER_MAX_CHARGE_POWER["max"]
            c.CHARGER_MAX_DISCHARGE_POWER = self.SETTING_CHARGER_MAX_DISCHARGE_POWER["max"]

        if kwargs is not None and kwargs.get('run_once', False):
            # To prevent a loop
            return
        await self.__collect_action_triggers(source="changed charger_settings")

    async def __read_and_process_notification_settings(self, entity=None, attribute=None, old=None, new=None,
                                                       kwargs=None):
        callback_method = self.__read_and_process_notification_settings

        c.ADMIN_MOBILE_NAME = await self.__process_setting(
            setting_object=self.SETTING_ADMIN_MOBILE_NAME,
            callback=callback_method
        )
        if c.ADMIN_MOBILE_NAME not in c.NOTIFICATION_RECIPIENTS:
            message = f"The admin mobile name ***{c.ADMIN_MOBILE_NAME}*** in configuration is not a registered.<br/>" \
                      f"Please choose one in the settings view."
            self.log(f"Configuration error: {message}.")
            # TODO: Research if showing this only to admin users is possible.
            self.call_service('persistent_notification/create', title="Configuration error", message=message,
                              notification_id="notification_config_error_no_admin")
            c.ADMIN_MOBILE_NAME = c.NOTIFICATION_RECIPIENTS[0]

        c.ADMIN_MOBILE_PLATFORM = await self.__process_setting(
            setting_object=self.SETTING_ADMIN_MOBILE_PLATFORM,
            callback=callback_method
        )
        # Assume iOS as standard
        c.PRIORITY_NOTIFICATION_CONFIG = {"push": {"sound": {"critical": 1, "name": "default", "volume": 0.9}}}
        if c.ADMIN_MOBILE_PLATFORM.lower() == "android":
            c.PRIORITY_NOTIFICATION_CONFIG = {"ttl": 0, "priority": "high"}

        # These settings do not require any re-init, so do not call __collect_action_triggers()

    async def __read_and_process_general_settings(self, entity=None, attribute=None, old=None, new=None, kwargs=None):
        callback_method = self.__read_and_process_general_settings

        c.CAR_CONSUMPTION_WH_PER_KM = await self.__process_setting(
            setting_object=self.SETTING_CAR_CONSUMPTION_WH_PER_KM,
            callback=callback_method
        )
        c.CAR_MAX_CAPACITY_IN_KWH = await self.__process_setting(
            setting_object=self.SETTING_CAR_MAX_CAPACITY_IN_KWH,
            callback=callback_method
        )
        c.CAR_MIN_SOC_IN_PERCENT = await self.__process_setting(
            setting_object=self.SETTING_CAR_MIN_SOC_IN_PERCENT,
            callback=callback_method
        )
        c.CAR_MAX_SOC_IN_PERCENT = await self.__process_setting(
            setting_object=self.SETTING_CAR_MAX_SOC_IN_PERCENT,
            callback=callback_method
        )
        c.ALLOWED_DURATION_ABOVE_MAX_SOC = await self.__process_setting(
            setting_object=self.SETTING_ALLOWED_DURATION_ABOVE_MAX_SOC_IN_HRS,
            callback=callback_method
        )

        c.CAR_MIN_SOC_IN_KWH = c.CAR_MAX_CAPACITY_IN_KWH * c.CAR_MIN_SOC_IN_PERCENT / 100
        c.CAR_MAX_SOC_IN_KWH = c.CAR_MAX_CAPACITY_IN_KWH * c.CAR_MAX_SOC_IN_PERCENT / 100

        await self.__collect_action_triggers(source="changed general_settings")

    async def __read_and_process_calendar_client_settings(self, entity=None, attribute=None, old=None, new=None,
                                                          kwargs=None):
        self.log("__read_and_process_calendar_client_settings called")

        callback_method = self.__read_and_process_calendar_client_settings

        tmp = await self.__process_setting(
            setting_object=self.SETTING_CAR_CALENDAR_SOURCE,
            callback=None
        )
        self.log(f"__read_and_process_calendar_client_settings CAR_CALENDAR_SOURCE: {tmp}")

        if c.CAR_CALENDAR_SOURCE != tmp:
            # TODO: Source has changed; cancel listeners
            pass

        c.CAR_CALENDAR_SOURCE = tmp
        if c.CAR_CALENDAR_SOURCE == "Direct caldav source":
            c.CALENDAR_ACCOUNT_INIT_URL = await self.__process_setting(
                setting_object=self.SETTING_CALENDAR_ACCOUNT_INIT_URL,
                callback=callback_method
            )
            c.CALENDAR_ACCOUNT_USERNAME = await self.__process_setting(
                setting_object=self.SETTING_CALENDAR_ACCOUNT_USERNAME,
                callback=callback_method
            )
            c.CALENDAR_ACCOUNT_PASSWORD = await self.__process_setting(
                setting_object=self.SETTING_CALENDAR_ACCOUNT_PASSWORD,
                callback=callback_method
            )
            c.CAR_CALENDAR_NAME = await self.__process_setting(
                setting_object=self.SETTING_CAR_CALENDAR_NAME,
                callback=None
            )  # Callback here is none as it will be set from init_car_calendar
        else:
            c.INTEGRATION_CALENDAR_ENTITY_NAME = await self.__process_setting(
                setting_object=self.SETTING_INTEGRATION_CALENDAR_ENTITY_NAME,
                callback=None
            )
            self.log(
                f"__read_and_process_calendar_client_settings c.INTEGRATION_CALENDAR_ENTITY_NAME: {c.INTEGRATION_CALENDAR_ENTITY_NAME}")

        await self.__collect_action_triggers(source="changed calendar settings")

    async def __read_and_process_fm_client_settings(self, entity=None, attribute=None, old=None, new=None, kwargs=None):
        # Split for future when the python lib fm_client is used: that needs to be re-inited
        self.log("__read_and_process_fm_client_settings called")

        callback_method = self.__read_and_process_fm_client_settings
        c.FM_ACCOUNT_USERNAME = await self.__process_setting(
            setting_object=self.SETTING_FM_ACCOUNT_USERNAME,
            callback=callback_method
        )
        c.FM_ACCOUNT_PASSWORD = await self.__process_setting(
            setting_object=self.SETTING_FM_ACCOUNT_PASSWORD,
            callback=callback_method
        )
        c.FM_BASE_URL = await self.__process_setting(
            setting_object=self.SETTING_FM_BASE_URL,
            callback=callback_method
        )

        # Set all FM related constants based upon the base url
        c.FM_BASE_API_URL = c.FM_BASE_URL + "/api/"

        # URL for checking if API is alive
        # https://flexmeasures.seita.nl/api/ops/ping
        c.FM_PING_URL = c.FM_BASE_API_URL + "ops/ping"

        # URL for authentication on FM
        # https://flexmeasures.seita.nl/api/requestAuthToken
        c.FM_AUTHENTICATION_URL = c.FM_BASE_API_URL + "requestAuthToken"

        # URL for retrieval of the schedules
        # https://flexmeasures.seita.nl/api/v3_0/sensors/XX/schedules/trigger
        # https://flexmeasures.seita.nl/api/v3_0/sensors/XX/schedules/SI
        # Where XX is the sensor_id and SI is the schedule_id
        c.FM_SCHEDULE_URL = c.FM_BASE_API_URL + c.FM_API_VERSION + "/sensors/"
        c.FM_SCHEDULE_SLUG = "/schedules/"
        c.FM_SCHEDULE_TRIGGER_SLUG = c.FM_SCHEDULE_SLUG + "trigger"

        # URL for getting data for the chart:
        # https://flexmeasures.seita.nl/api/dev/sensor/XX/chart_data/
        # Where XX is the sensor_id
        c.FM_GET_DATA_URL = c.FM_BASE_API_URL + "dev/sensor/"
        c.FM_GET_DATA_SLUG = "/chart_data/"

        # URL for sending metering data to FM:
        # https://flexmeasures.seita.nl/api/v3_0/sensors/data
        c.FM_SET_DATA_URL = c.FM_BASE_API_URL + c.FM_API_VERSION + "/sensors/data"

        c.FM_ACCOUNT_POWER_SENSOR_ID = await self.__process_setting(
            setting_object=self.SETTING_FM_ACCOUNT_POWER_SENSOR_ID,
            callback=callback_method
        )
        c.FM_ACCOUNT_AVAILABILITY_SENSOR_ID = await self.__process_setting(
            setting_object=self.SETTING_FM_ACCOUNT_AVAILABILITY_SENSOR_ID,
            callback=callback_method
        )
        c.FM_ACCOUNT_SOC_SENSOR_ID = await self.__process_setting(
            setting_object=self.SETTING_FM_ACCOUNT_SOC_SENSOR_ID,
            callback=callback_method
        )
        c.FM_ACCOUNT_COST_SENSOR_ID = await self.__process_setting(
            setting_object=self.SETTING_FM_ACCOUNT_COST_SENSOR_ID,
            callback=callback_method
        )

        c.OPTIMISATION_MODE = await self.__process_setting(
            setting_object=self.SETTING_OPTIMISATION_MODE,
            callback=callback_method
        )
        c.ELECTRICITY_PROVIDER = await self.__process_setting(
            setting_object=self.SETTING_ELECTRICITY_PROVIDER,
            callback=callback_method
        )

        # If the price and emissions data is provided to FM by V2G Liberty (noe EPEX markets)
        # this is labelled as "self_provided".
        # TODO: Cancel listers for none-relevants
        if c.ELECTRICITY_PROVIDER == "self_provided":
            c.FM_PRICE_PRODUCTION_SENSOR_ID = await self.__process_setting(
                setting_object=self.SETTING_FM_PRICE_PRODUCTION_SENSOR_ID,
                callback=callback_method
            )
            c.FM_PRICE_CONSUMPTION_SENSOR_ID = await self.__process_setting(
                setting_object=self.SETTING_FM_PRICE_CONSUMPTION_SENSOR_ID,
                callback=callback_method
            )
            c.FM_EMISSIONS_SENSOR_ID = await self.__process_setting(
                setting_object=self.SETTING_FM_EMISSIONS_SENSOR_ID,
                callback=callback_method
            )
            c.UTILITY_CONTEXT_DISPLAY_NAME = await self.__process_setting(
                setting_object=self.SETTING_UTILITY_CONTEXT_DISPLAY_NAME,
                callback=callback_method
            )
        else:
            context = c.DEFAULT_UTILITY_CONTEXTS.get(
                c.ELECTRICITY_PROVIDER,
                c.DEFAULT_UTILITY_CONTEXTS["nl_generic"],
            )
            self.log(f"De utility_context is: {context}.")
            # ToDo: Notify user if fallback "nl_generic" is used..
            c.FM_PRICE_PRODUCTION_SENSOR_ID = context["production-sensor"]
            c.FM_PRICE_CONSUMPTION_SENSOR_ID = context["consumption-sensor"]
            c.FM_EMISSIONS_SENSOR_ID = context["emissions-sensor"]
            c.UTILITY_CONTEXT_DISPLAY_NAME = context["display-name"]
            self.log(f"v2g_globals FM_PRICE_PRODUCTION_SENSOR_ID: {c.FM_PRICE_PRODUCTION_SENSOR_ID}.")
            self.log(f"v2g_globals FM_PRICE_CONSUMPTION_SENSOR_ID: {c.FM_PRICE_CONSUMPTION_SENSOR_ID}.")
            self.log(f"v2g_globals FM_EMISSIONS_SENSOR_ID: {c.FM_EMISSIONS_SENSOR_ID}.")
            self.log(f"v2g_globals UTILITY_CONTEXT_DISPLAY_NAME: {c.UTILITY_CONTEXT_DISPLAY_NAME}.")

        # Only for these electricity_providers do we take the VAT and markup from the secrets into account.
        # For others, we expect netto prices (including VAT and Markup).
        # If self_provided data also includes VAT and markup the values in secrets can
        # be set to 1 and 0 respectively to achieve the same result as here.
        if c.ELECTRICITY_PROVIDER in ["self_provided", "nl_generic", "no_generic"]:
            c.ENERGY_PRICE_VAT = await self.__process_setting(
                setting_object=self.SETTING_ENERGY_PRICE_VAT,
                callback=callback_method
            )
            c.ENERGY_PRICE_MARKUP_PER_KWH = await self.__process_setting(
                setting_object=self.SETTING_ENERGY_PRICE_MARKUP_PER_KWH,
                callback=callback_method
            )

        await self.__collect_action_triggers(source="changed fm_settings")

    async def __collect_action_triggers(self, source: str):
        # Prevent parallel calls to set_next_cation and always wait a little as
        # the user likely changes several settings at a time.
        # This also prevents calling V2G Liberty too early when it has not
        # completed initialisation yet.

        if self.collect_action_handle is None:
            # This is the initial, init has not finished yet
            return
        if self.info_timer(self.collect_action_handle):
            await self.cancel_timer(self.collect_action_handle, True)
        self.collect_action_handle = await self.run_in(self.__collective_action, delay=15)

    async def __collective_action(self, v2g_args=None):
        await self.fm_client.initialise_fm_settings()
        await self.evse_client.initialise_charger(v2g_args="changed settings")
        await self.v2g_main_app.set_next_action(v2g_args="changed settings")

    async def process_max_power_settings(self, min_acceptable_charge_power: int, max_available_charge_power: int):
        """To be called from modbus_evse_client to check if setting in the charger
           is lower than the setting by the user.
        """
        self.log(f'process_max_power_settings called with power {max_available_charge_power}.')
        self.SETTING_CHARGER_MAX_CHARGE_POWER['max'] = max_available_charge_power
        self.SETTING_CHARGER_MAX_CHARGE_POWER['min'] = min_acceptable_charge_power
        self.SETTING_CHARGER_MAX_DISCHARGE_POWER['max'] = max_available_charge_power
        self.SETTING_CHARGER_MAX_DISCHARGE_POWER['min'] = min_acceptable_charge_power

        # For showing this maximum in the UI.
        await self.set_state("input_text.charger_max_available_power", state=max_available_charge_power)

        kwargs = {'run_once': True}
        await self.__read_and_process_charger_settings(kwargs=kwargs)

    def create_persistent_notification(self, message: str, title: str, notification_id: str):
        self.call_service(
            'persistent_notification/create',
            title=title,
            message=message,
            notification_id=notification_id
        )


def time_mod(time, delta, epoch=None):
    """From https://stackoverflow.com/a/57877961/13775459"""
    if epoch is None:
        epoch = datetime(1970, 1, 1, tzinfo=time.tzinfo)
    return (time - epoch) % delta


def time_round(time, delta, epoch=None):
    """From https://stackoverflow.com/a/57877961/13775459"""
    mod = time_mod(time, delta, epoch)
    if mod < (delta / 2):
        return time - mod
    return time + (delta - mod)


def time_ceil(time, delta, epoch=None):
    """From https://stackoverflow.com/a/57877961/13775459"""
    mod = time_mod(time, delta, epoch)
    if mod:
        return time + (delta - mod)
    return time
