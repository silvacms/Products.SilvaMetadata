"""
Marker Interfaces
author: kapil thangavelu <k_vertigo@objectrealms.net>
"""
from zope.interface import Interface

class IAcquiredUpdater(Interface):
    """
    Do any (catalog) updates that may be necessary after setting acquired
    metadata for an object.

    This is a pure hook: SilvaMetadata and even the Silva core at present
    do not provide any IAcquiredUpdater adapters. An extension to Silva
    may however register one.
    """
    def update():
        """Perform the update.
        """
        
class IPortalMetadata(Interface):
    pass

#################################
# Metadata Tool/Service Interface
#################################
class IMetadataTool(IPortalMetadata):
    pass

#################################
# Base Building Blocks
#################################

class IMetadataCollection(Interface):
    pass

class IOrderedContainer(Interface):

    def moveObject(id, position):
        """
        move an object with the given an id to the specified
        position.
        """
    def moveObjectUp(id, steps=1):
        """
        move an object with the given id up the ordered list
        the given number of steps
        """

    def moveObjectDown(id, steps=1):
        """
        move an object with the given id down the ordered list
        the given number of steps
        """

    def getObjectPosition(id):
        """
        given an object id return its position in the ordered list
        """

class IMetadataSet(IOrderedContainer):
    pass

class IMetadataElement(Interface):
    pass

#################################
# Adapter Provided Functionality
#################################
# all of these operate on a set basis.

class IMetadataSetExporter(Interface):
    pass

class IMetadataForm(Interface):
    pass

class IMetadataValidation(Interface):
    pass

class IMetadataStorage(Interface):
    pass
