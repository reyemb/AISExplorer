import urllib.parse
from collections.abc import Iterable
from aisexplorer.Exceptions import (
    NotSupportedKeyError,
    NotSupportedKeyTypeError,
    NotSupportedArgumentType,
)


class BaseFilter:
    """Base class for all filters."""

    def __init__(self, key, value, expected_type):
        if not isinstance(value, expected_type):
            raise NotSupportedKeyTypeError(key, type(value), expected_type)
        self.key = key
        self.value = value

    def to_query(self):
        raise NotImplementedError("Must implement to_query in subclasses.")


class StrFilter(BaseFilter):
    """Filter for string type queries."""

    dict_var = {
        "vessel_name": "shipname",
        "destination_port": "recognized_next_port_in",
        "reported_dest": "reported_destinations",
        "callsign": "callsign",
        "current_port": "current_port_in",
    }

    def __init__(self, key, value):
        super().__init__(key, value, str)

    def to_query(self):
        query_key = self.dict_var[self.key]
        if self.key in ["vessel_name", "recognized_next_port_in"]:
            operator = "begins"
        else:
            operator = "eq"
        return f"&{query_key}|{operator}|{query_key}={self.value}"


class SliderFilter:
    _dict_var = {
        "lon": "lon_of_latest_position_between",
        "lat": "lat_of_latest_position_between",
        "latest_report": "time_of_latest_position_between",
        "speed": "speed_between",
        "course": "course_between",
        "dwt": "dwt_between",
        "built": "year_of_build_between",
        "length": "length_between",
        "width": "width_between",
        "draught": "draught_between",
    }

    def __init__(self, key: str, values: Iterable):
        if not isinstance(values, Iterable) or isinstance(values, str):
            raise NotSupportedArgumentType(
                f"The values for {key} must be an iterable of two numbers."
            )
        if len(values) != 2:
            raise ValueError(
                f"The values for {key} must be an iterable of exactly two elements."
            )
        self.key = key
        self.value = [str(value) for value in values]

    def to_query(self) -> str:
        query_key = self._dict_var.get(self.key)
        if query_key is None:
            raise NotSupportedKeyError(
                f"The key '{self.key}' is not supported for a SliderFilter."
            )

        if self.key == "latest_report":
            operator = "gte"
        elif self.key == "course":
            operator = "range_circle"
        else:
            operator = "range"

        return f"&{query_key}|{operator}|{query_key}={','.join(self.value)}"


class IntFilter:
    _dict_var = {
        "imo": "imo",
        "emi": "emi",
        "mmsi": "mmsi",
    }

    def __init__(self, key: str, value: int):
        if not isinstance(value, int):
            raise NotSupportedKeyTypeError(f"The value for {key} must be an integer.")
        self.key = key
        self.value = value

    def to_query(self) -> str:
        query_key = self._dict_var.get(self.key)
        if query_key is None:
            raise NotSupportedKeyError(
                f"The key '{self.key}' is not supported for an IntFilter."
            )
        return f"&{query_key}|eq|{query_key}={self.value}"


class ListFilter:
    _dict_var = {
        "flag": "flag_in",
        "vessel_type": "ship_type_in",
        "global_area": "area_in",
        "local_area": "area_local_in",
        "nav_status": "navigational_status_in",
        "current_port_country": "current_port_country_in",
        "fleets": "fleet_in",
    }

    def __init__(self, key: str, value):
        if not isinstance(value, (list, dict, str)):
            raise NotSupportedKeyTypeError(
                f"The value for {key} must be a list, dictionary, or string."
            )
        self.key = key
        self.operator = "in"
        if isinstance(value, dict):
            self.value = value.get("values")
            self.operator = value.get("operator", "in")
        else:
            self.value = value

    def to_query(self) -> str:
        query_key = self._dict_var.get(self.key)
        if query_key is None:
            raise NotSupportedKeyError(
                f"The key '{self.key}' is not supported for a ListFilter."
            )
        if isinstance(self.value, list):
            value_str = ",".join(map(str, self.value))
        else:
            value_str = str(self.value)
        return f"&{query_key}|{self.operator}|{value_str}"


class FleetFilter:
    def __init__(self, user_fleets: Iterable[Iterable[str]]):
        if not all(
            isinstance(fleet, (list, tuple)) and len(fleet) == 2
            for fleet in user_fleets
        ):
            raise ValueError(
                "user_fleets must be an iterable of iterables each with two strings."
            )
        self.user_fleets = user_fleets

    def to_referer_query(self) -> str:
        fleet_names = ",".join(
            urllib.parse.quote_plus(fleet[1]) for fleet in self.user_fleets
        )
        fleet_ids = ",".join(
            urllib.parse.quote_plus(fleet[0]) for fleet in self.user_fleets
        )
        return f"&fleet_in|in|{fleet_names}|fleet_in={fleet_ids}"

    def to_request_query(self) -> str:
        fleet_ids = ",".join(
            urllib.parse.quote_plus(fleet[0]) for fleet in self.user_fleets
        )
        return f"&fleet_in={fleet_ids}"


class Filters:
    _possible_filters = {
        "imo": IntFilter,
        "emi": IntFilter,
        "mmsi": IntFilter,
        "vessel_name": StrFilter,
        "callsign": StrFilter,
        "current_port": StrFilter,
        "reported_dest": StrFilter,
        "destination_port": StrFilter,
        "latest_report": SliderFilter,
        "lat": SliderFilter,
        "lon": SliderFilter,
        "speed": SliderFilter,
        "course": SliderFilter,
        "dwt": SliderFilter,
        "built": SliderFilter,
        "length": SliderFilter,
        "width": SliderFilter,
        "draught": SliderFilter,
        "flag": ListFilter,
        "vessel_type": ListFilter,
        "global_area": ListFilter,
        "local_area": ListFilter,
        "nav_status": ListFilter,
        "current_port_country": ListFilter,
        "fleets": ListFilter,
    }

    def __init__(self, **kwargs: dict):
        self.filters = {
            key: filter_class(key, value)
            for key, value in kwargs.items()
            if (filter_class := self._possible_filters.get(key))
        }

        unsupported_keys = set(kwargs) - self.filters.keys()
        if unsupported_keys:
            raise NotSupportedKeyError(f"Unsupported filter keys: {unsupported_keys}.")

    def to_query(self, ignore_filter=None) -> str:
        """Generate a query string from filters, excluding any specified in ignore_filter."""
        if ignore_filter is not None:
            if isinstance(ignore_filter, str):
                ignore_filter = {ignore_filter}
            elif not isinstance(ignore_filter, Iterable) or isinstance(
                ignore_filter, str
            ):
                raise ValueError(
                    "ignore_filter must be a string or an iterable of strings."
                )

        query_parts = [
            filter_instance.to_query()
            for key, filter_instance in self.filters.items()
            if ignore_filter is None or key not in ignore_filter
        ]
        return "&".join(query_parts).replace("&&", "&")
