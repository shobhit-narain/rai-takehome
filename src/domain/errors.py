from __future__ import annotations


class DomainError(Exception):
    pass


class InvalidStateTransitionError(DomainError):
    pass


class PolicyViolationError(DomainError):
    pass


class InsufficientBalanceError(DomainError):
    pass


class ReconciliationRequiredError(DomainError):
    pass
