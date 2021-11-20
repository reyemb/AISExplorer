import difflib


class MalformedFunctionError(Exception):
    def __init__(self, message):
        super().__init__(f"Function is malformed\n{message}")


class NotSupportedParameterTypeError(MalformedFunctionError):
    def __init__(self, parameter, supported_types, given_type):
        super().__init__(f"{parameter} does only support the following instances {', '.join(supported_types)} but {given_type} has been given")


class NotSupportedParameterError(MalformedFunctionError):
    def __init__(self, parameter, supported_arguments, given_argument):
        super().__init__(f"{parameter} only accepts the following arguments {','.join(supported_arguments)}, but {given_argument} was given. Did you mean {difflib.get_close_matches(given_argument, supported_arguments)}")