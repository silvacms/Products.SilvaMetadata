from AccessControl import ClassSecurityInfo
from ComputedAttribute import ComputedAttribute
from OFS.SimpleItem import SimpleItem
from OFS.Folder import Folder
from Globals import DTMLFile, InitializeClass
from Interface import Base as Interface
from ZODB.PersistentMapping import PersistentMapping

from Compatiblity import getToolByName, UniqueObject

# py2.2.2 forward decl
try:
    True, False
except:
    True = 1
    False = 0
    
