import warnings
from collections.abc import Iterable
from aisexplorer.Exceptions import NotSupportedKeyError, NotSupportedKeyTypeError, NotSupportedArgumentType


class StrFilter:
    dict_var = {
        'vessel_name': 'shipname',
        'destination_port': 'recognized_next_port_in',
        'reported_dest': 'reported_destinations',
        'callsign': 'callsign',
        'current_port': 'current_port_in'
    }

    def __init__(self, key, value):
        self.key = key
        if not isinstance(value, str):
            raise NotSupportedKeyTypeError(key, type(value), [str])
        self.value = value

    def to_query(self):
        if self.key == 'vessel_name':
            return f"{self.key}|begins|{self.key}={self.value[0], self.value[1]}"
        elif self.key == 'recognized_next_port_in':
            return f"{self.key}|begins|{self.key}_name={self.value[0], self.value[1]}"
        elif self.key == 'callsign':
            return f"{self.key}|eq|{self.key}={self.value[0], self.value[1]}"
        elif self.key == 'report_dest':
            return f"{self.key}|eq|{self.key}={self.value[0], self.value[1]}"
        elif self.key == 'current_port':
            return f"{self.key}|begins||{self.key}={self.value[0], self.value[1]}"
        return ""


class SliderFilter:
    dict_var = {
        'lon': 'lon_of_latest_position_between',
        'lat': 'lat_of_latest_position_between',
        'latest_report': 'time_of_latest_position_between',
        'speed': 'speed_between',
        'course': 'course_between',
        'dwt': 'dwt_between',
        'built': 'year_of_build_between',
        'length': 'length_between',
        'width': 'width_between',
        'draught': 'draught_between'
    }

    def __init__(self, key, values):
        self.key = key
        if isinstance(values, str) or not isinstance(values, Iterable):
            raise NotSupportedKeyTypeError(key, type(values), [Iterable])
        if len(values) != 2:
            raise NotSupportedArgumentType(key, 2, len(values))
        self.value = [str(value) for value in values]

    def to_query(self):
        if self.key == 'latest_report':
            return f"{self.key}|gte|{self.key}={self.value[0], self.value[1]}"
        elif self.key == 'course':
            return f"{self.key}|range_circle|{self.key}={self.value[0], self.value[1]}"
        else:
            return f"{self.key}|range|{self.key}={self.value[0], self.value[1]}"


class IntFilter:
    dict_var = {
        'imo': '',
        'emi': 'emi',
        'mmsi': 'mmsi',
    }

    def __init__(self, key, value):
        if not isinstance(value, int):
            raise NotSupportedKeyTypeError(key, type(value), [int])
        self.key = key
        self.value = value

    def to_query(self):
        return f"&{self.key}|eq|{self.key}={self.value}"


class ListFilter:
    dict_var = {
        'flag': 'flag_in',
        'vessel_type': 'ship_type_in',
        'global_area': 'area_in',
        'local_area': 'area_local_in',
        'nav_status': 'navigational_status_in',
        'current_port_country': 'current_port_country_in',
    }

    def __init__(self, key, value):
        if not isinstance(value, (list, dict)):
            raise NotSupportedKeyTypeError(key, type(value), [list, dict])
        if isinstance(value, list):
            warnings.warn("List has been given by default filter will filter all elements IN the list. If you want to "
                          "to filter for elements which are not in the list use a dict instead")
            self.value = value
            self.operator = "in"
        else:
            self.value = value['values']
            self.value = value['operator']
        self.key = key

    def to_query(self):
        return f"&{self.key}|{self.operator}|{self.key}={self.value}"


class Filters:
    possible_filters = {
        'imo': IntFilter,
        'emi': IntFilter,
        'mmsi': IntFilter,
        'vessel_name': StrFilter,
        'callsign': StrFilter,
        'current_port': StrFilter,
        'reported_dest': StrFilter,
        'destination_port': StrFilter,
        'latest_report': SliderFilter,
        'lat': SliderFilter,
        'lon': SliderFilter,
        'speed': SliderFilter,
        'course': SliderFilter,
        'dwt': SliderFilter,
        'built': SliderFilter,
        'length': SliderFilter,
        'width': SliderFilter,
        'draught': SliderFilter,
        'flag': ListFilter,
        'vessel_type': ListFilter,
        'global_area': ListFilter,
        'local_area': ListFilter,
        'nav_status': ListFilter,
        'current_port_country': ListFilter
    }

    def __init__(self, **kwargs):
        self.filters = []
        for key, value in kwargs.items():
            if key not in self.possible_filters:
                raise NotSupportedKeyError(key, list(self.possible_filters))
            self.filters.append(self.possible_filters[key](key, value))

    def to_query(self):
        res_str = ""
        for custom_filter in self.filters:
            res_str += custom_filter.to_query()
        return res_str
