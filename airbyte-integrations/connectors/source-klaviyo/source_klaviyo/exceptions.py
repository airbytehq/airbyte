class KlaviyoBackoffError(Exception):
    """An exception which is raised when 'retry-after' time is longer than 'max_time' specified"""
