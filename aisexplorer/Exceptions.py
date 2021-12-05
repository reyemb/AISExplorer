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


class MalformedFilterError(Exception):
    def __init__(self, message):
        super().__init__(f"Filter is malformed\n{message}")


class NotSupportedKeyError(MalformedFilterError):
    def __init__(self, supported_keys, given_key):
        super().__init__(f"The following keys are accepted: {','.join(supported_keys)}, but {given_key} was given. Did you mean {difflib.get_close_matches(given_key, supported_keys)}")


class NotSupportedKeyTypeError(MalformedFilterError):
    def __init__(self, key, value, accept_types):
        super().__init__(
            f"For the {key} the following values types are accepted: {','.join(accept_types)}, but {value} was given.")


class NotSupportedArgumentType(MalformedFilterError):
    def __init__(self, key, given_form, accepted_form):
        super().__init__(
            f"For the Filter {key} the arguments should have a length of {accepted_form} but {given_form} was given.")


