from django.db import models
from rest_framework import permissions


class TenantQuerySet(models.QuerySet):
    def for_user(self, user):
        if not user.is_authenticated:
            return self.none()
        # Assume every tenant model has a 'store' foreign key,
        # and Store has an 'owner' foreign key.
        return self.filter(store__owner=user)


class TenantManager(models.Manager):
    def get_queryset(self):
        return TenantQuerySet(self.model, using=self._db)

    def for_user(self, user):
        return self.get_queryset().for_user(user)


class IsStoreOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object's store to access it.
    """

    def has_object_permission(self, request, view, obj):
        # The object must have a 'store' attribute
        if hasattr(obj, "store"):
            return obj.store.owner == request.user
        # Or if the object itself is a store
        if hasattr(obj, "owner"):
            return obj.owner == request.user
        return False
