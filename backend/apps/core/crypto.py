from cryptography.fernet import Fernet
from django.conf import settings
from django.db import models


def get_fernet():
    key = settings.FIELD_ENCRYPTION_KEY
    if not key:
        raise ValueError("FIELD_ENCRYPTION_KEY must be set in settings.")
    return Fernet(key.encode("utf-8"))


def encrypt_value(value: str) -> str:
    if not value:
        return value
    f = get_fernet()
    return f.encrypt(value.encode("utf-8")).decode("utf-8")


def decrypt_value(value: str) -> str:
    if not value:
        return value
    f = get_fernet()
    return f.decrypt(value.encode("utf-8")).decode("utf-8")


class EncryptedTextField(models.TextField):
    """
    A field that encrypts data before saving to the DB and decrypts it when retrieving.
    """

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        try:
            return decrypt_value(value)
        except Exception as e:
            # Fallback for unencrypted data or incorrect key
            import logging
            logging.getLogger(__name__).warning("Failed to decrypt value: %s", e)
            return value

    def to_python(self, value):
        if isinstance(value, str):
            return value
        return super().to_python(value)

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value is None or value == "":
            return value
        return encrypt_value(value)
