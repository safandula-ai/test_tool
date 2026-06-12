from __future__ import annotations

from faker import Faker


faker = Faker()


def unique_email() -> str:
    """Generate a unique email address for isolated test data."""
    return faker.unique.email()


def unique_name() -> str:
    """Generate a realistic person name for test data."""
    return faker.name()
