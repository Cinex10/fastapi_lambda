class OrderAlreadyExistsException(Exception):
    """Exception raised for order already exists errors."""


class OrderNotFoundException(Exception):
    """Exception raised for order not found errors."""


class UnauthorizedException(Exception):
    """Exception raised for unauthorized errors."""


class UnauthenticatedException(Exception):
    """Exception raised for unauthenticated errors."""


class InvalidCredentialsException(Exception):
    """Exception raised for invalid credentials errors."""
