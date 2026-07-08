from __future__ import annotations


class UpstreamError(Exception):
    pass


class UpstreamTimeoutError(UpstreamError):
    pass


class UpstreamAuthError(UpstreamError):
    pass


class UpstreamRateLimitError(UpstreamError):
    pass


class UpstreamValidationError(UpstreamError):
    pass


class RetriableUpstreamError(UpstreamError):
    pass
