"""
Metadata Elements
Author: kapil thangavelu <k_vertigo@objectrealms.net>
"""

from AccessControl import getSecurityManager
from Exceptions import NoContext, ConfigurationError
from FormulatorField import getFieldFactory
from Guard import Guard
from Interfaces import IMetadataElement
from ZopeImports import *

_marker = []

encoding = 'UTF-8'

class MetadataElement(SimpleItem):
    """
    Property Bag For Element Policies
    """
    
    meta_type = 'Metadata Element'

    __implements__ = IMetadataElement

    #################################
    # element policy properties
    #################################
    
    read_only_p = False
    index_p = False
    index_type = None
    field_type = None

    ## defer to formulator for now
    use_default_p = True
    #required_p = False    
    #default = None
    
    ## out of scope for initial impl
    #export_p = True
    #enforce_vocabulary_p = True
    
    manage_options = (
        {'label':'Settings',
         'action':'elementSettingsForm'},
        {'label':'Guards',
         'action':'elementGuardForm'},
        {'label':'Field',
         'action':'field/manage_main'},        
        )

    elementSettingsForm = DTMLFile('ui/ElementPolicyForm', globals())
    elementGuardForm   = DTMLFile('ui/ElementGuardForm', globals())

    security = ClassSecurityInfo()
    
    def __init__(self, id, **kw):
        self.id = id
        self.read_guard = Guard()
        self.write_guard = Guard()

    def editElementGuards(self, read_guard, write_guard, RESPONSE=None):

        self.read_guard.changeFromProperties(read_guard)
        self.write_guard.changeFromProperties(write_guard)
        
        if RESPONSE is not None:
            RESPONSE.redirect('manage_workspace')

    def editElementPolicy(self,
                          field_type = None,
                          index_type = None,
                          index_p = None,
                          read_only_p = None,
                          use_default_p = None,
                          RESPONSE = None
                          ):
        """
        edit an element's policy
        """

        if index_type is not None:
            ms = self.getMetadataSet()
            if ms.isInitialized():
                raise ConfigurationError("Not Allowed Set Already initialized")

        if field_type is not None:
            ms = self.getMetadataSet()
            if ms.isInitialized():
                raise ConfigurationError("Not Allowed Set Already initialized")

        field_type = field_type or self.field_type
        index_type = index_type or self.index_type
        
        if index_p is None:
            index_p = self.index_p


        if use_default_p is None:
            use_default_p = self.use_default_p

        if read_only_p is None:
            read_only_p = self.read_only_p
        
        if field_type != self.field_type:
            try:
                factory = getFieldFactory(field_type)
            except KeyError:
                raise ConfigurationError("invalid field type %s"%field_type)
            self.field = factory( self.getId() )
            self.field.field_record = self.getMetadataSet().getId()
            self.field_type = field_type
            self.field.values['unicode']=1
            
        if index_type is not None:
            if index_type in self.getMetadataSet().listIndexTypes():
                self.index_type = index_type
            else:
                raise ConfigurationError("invalid index type %s"%index_type)

        # need to cascacde this so we can create indexes at the set level
        self.index_p = not not index_p
        self.read_only_p = not not read_only_p
        self.use_default_p = not not use_default_p

        if RESPONSE is not None:
            return RESPONSE.redirect('manage_workspace')
    
    def validate(self, data):
        return self.field.validate(data)

    def title(self):
        return self.field.get_value('title')

    def isViewable(self, content):
        """
        is this element viewable for the content object
        """
        return self.read_guard.check(getSecurityManager(), self, content)

    def isEditable(self, content):
        """
        is this element editable for the content object
        """
        return self.write_guard.check(getSecurityManager(), self, content)

    def renderView(self, value):
        """
        render the element given a particular element value
        """
        return self.field.render_view(value)

    def renderEdit(self, value):
        """
        render the element as a form field given a particular value
        """
        return self.field.render(value)

    def isRequired(self):
        return self.field.is_required()

    def getDefault(self):
        """
        return the default value for this element
        """
        return self.field.get_value('default')
           
    ## little hack to get formulator fields to do unicode
    def get_form_encoding(self):
        return encoding
       
InitializeClass(MetadataElement)

def ElementFactory(id, **kw):

    return MetadataElement(id, **kw)
    

        
