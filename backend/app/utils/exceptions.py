class ResumeIQError(Exception):
    """Base application exception for expected domain errors."""


class EmailAlreadyRegistered(ResumeIQError):
    """Raised when a registration email is already in use."""


class InvalidCredentials(ResumeIQError):
    """Raised when login credentials cannot be verified."""
