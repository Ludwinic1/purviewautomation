import sys

from purviewautomation.auth import (
    AzIdentityAuthentication,
    ServicePrincipalAuthentication,
)
from purviewautomation.collections import PurviewCollections

MODULE_OBJECTS = dir()


def test_import_modules():
    assert "purviewautomation" in sys.modules
    assert "purviewautomation.auth" in sys.modules
    assert "purviewautomation.collections" in sys.modules


def test_import_classes():
    assert "AzIdentityAuthentication" in MODULE_OBJECTS
    assert "ServicePrincipalAuthentication" in MODULE_OBJECTS
    assert "PurviewCollections" in MODULE_OBJECTS