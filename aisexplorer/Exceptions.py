import difflib


class MalformedFunctionError(Exception):
    """Exception raised for errors in the formation of a function."""

    def __init__(self, message: str):
        """
        Args:
            message: Explanation of the error.
        """
        super().__init__(f"Function is malformed\n{message}")


class NotSupportedParameterTypeError(MalformedFunctionError):
    """Exception raised for unsupported parameter types in a function."""

    def __init__(self, parameter: str, supported_types: list, given_type: type):
        """
        Args:
            parameter: The parameter that received the unsupported type.
            supported_types: A list of supported types for the parameter.
            given_type: The type of the argument that was provided.
        """
        message = (
            f"{parameter} does only support the following instances {', '.join(supported_types)} "
            f"but {given_type} has been given"
        )
        super().__init__(message)


class NotSupportedParameterError(MalformedFunctionError):
    """Exception raised for unsupported parameter values in a function."""

    def __init__(self, parameter: str, supported_arguments: list, given_argument: str):
        """
        Args:
            parameter: The parameter that received the unsupported value.
            supported_arguments: A list of supported arguments for the parameter.
            given_argument: The argument that was provided.
        """
        suggestion = difflib.get_close_matches(given_argument, supported_arguments)
        message = (
            f"{parameter} only accepts the following arguments {','.join(supported_arguments)}, "
            f"but {given_argument} was given. Did you mean {suggestion}?"
        )
        super().__init__(message)


class MalformedFilterError(Exception):
    """Exception raised for errors in the formation of a filter."""

    def __init__(self, message: str):
        """
        Args:
            message: Explanation of the error.
        """
        super().__init__(f"Filter is malformed\n{message}")


class NotSupportedKeyError(MalformedFilterError):
    """Exception raised for unsupported keys in a filter."""

    def __init__(self, supported_keys: list, given_key: str):
        """
        Args:
            supported_keys: A list of keys that are supported.
            given_key: The key that was used and is not supported.
        """
        suggestion = difflib.get_close_matches(given_key, supported_keys)
        message = (
            f"The following keys are accepted: {','.join(supported_keys)}, "
            f"but {given_key} was given. Did you mean {suggestion}?"
        )
        super().__init__(message)


class NotSupportedKeyTypeError(MalformedFilterError):
    """Exception raised for unsupported value types for a given key in a filter."""

    def __init__(self, key: str, value, accept_types: list):
        """
        Args:
            key: The key that was used in the filter.
            value: The value that was provided.
            accept_types: A list of accepted types for the value.
        """
        message = (
            f"For the {key} the following value types are accepted: {','.join(accept_types)}, "
            f"but {value} was given."
        )
        super().__init__(message)


class NotSupportedArgumentType(MalformedFilterError):
    """Exception raised for arguments of an unsupported form in a filter."""

    def __init__(self, key: str, given_form: int, accepted_form: int):
        """
        Args:
            key: The key that was used in the filter.
            given_form: The form/length of the arguments that was provided.
            accepted_form: The expected form/length of the arguments.
        """
        message = f"For the Filter {key} the arguments should have a length of {accepted_form} but {given_form} was given."
        super().__init__(message)


class NoResultsError(Exception):
    """Exception raised when no Results are given."""

    def __init__(self, message):
        super().__init__(message)


class CloudflareError(Exception):
    """Exception raised when Cloudflare detects unusual behavior."""

    def __init__(self):
        super().__init__("Cloudflare detected unusual behaviour")


class UserNotLoggedInError(Exception):
    """Exception raised when a user tries to perform an action that requires being logged in."""

    def __init__(self):
        super().__init__("Function can only be used if the user is logged in")


class ProxiesNoLongerSupportedError(Exception):
    """Exception raised when a user tries to use proxies."""

    def __init__(self):
        super().__init__(
            "Since using Proxies results in an unreliable experience, they are no longer supported."
        )
