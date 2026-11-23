"""Own exceptions of the measurement package."""


class MeasurementError(Exception):
    """Base class for all errors of this package."""


class UnsupportedFormatError(MeasurementError):
    """There is no reader for the file format."""

    def __init__(self, file_format: str, supported_formats: list[str]):
        self.file_format = file_format
        self.supported_formats = supported_formats
        super().__init__(f"No reader for '{file_format}' files, supported are: {', '.join(supported_formats)}")


class MissingSignalError(MeasurementError):
    """A signal that every measurement needs is not in the file."""

    def __init__(self, signal: str):
        self.signal = signal
        super().__init__(f"The signal '{signal}' is missing in the file")


class InvalidMeasurementError(MeasurementError):
    """The signals were read, but they do not form a usable measurement (e.g. different lengths)."""


class NoGpsDataError(MeasurementError):
    """The measurement has no GPS position, e.g. a map can not be drawn."""
