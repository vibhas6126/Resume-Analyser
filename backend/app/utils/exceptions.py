class ResumeIQError(Exception):
    """Base application exception for expected domain errors."""


class EmailAlreadyRegistered(ResumeIQError):
    """Raised when a registration email is already in use."""


class InvalidCredentials(ResumeIQError):
    """Raised when login credentials cannot be verified."""


class InvalidResumeFile(ResumeIQError):
    """Raised when an uploaded resume is not a valid supported file."""


class ResumeNotFound(ResumeIQError):
    """Raised when a resume cannot be found for the current user."""


class ResumeParsingFailed(ResumeIQError):
    """Raised when text cannot be extracted from an uploaded resume."""
