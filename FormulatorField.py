"""
provides access to formulator field registry, and some monkey
patches to formulator field to allow easier reuse by metdata system

author: kapil thangavelu <k_vertigo@objectrealms.net>
"""
from Acquisition import aq_inner, aq_parent
from Interfaces import IMetadataElement

from Products.Formulator.FieldRegistry import FieldRegistry
from Products.Formulator.Field import Field

def getFieldFactory(fieldname):
    return FieldRegistry.get_field_class(fieldname)

def listFields():
    mapping = FieldRegistry.get_field_classes()
    field_types = mapping.keys()
    field_types.sort()
    return field_types

#################################
### We are the monkies 

def generate_field_key(self, validation=0):
    if self.field_record is None:
        return 'field_%s'%self.id
    elif validation:
        return self.id
    return '%s.%s:record'%(self.field_record, self.id)

def generate_subfield_key(self, id, validation=0):
    if self.field_record is None or validation:
        return 'subfield_%s_%s'%(self.id, id)
    return '%s.subfield_%s_%s:record'%(self.field_record, self.id, id)

def render(self, value=None, REQUEST=None):
    """ """
    return self._render_helper( self.generate_field_key(), value, REQUEST )

def render_from_request(self, REQUEST):
    """ """
    return self._render_helper( self.generate_field_key(), None, REQUEST )

def render_sub_field(self, id, value=None, REQUEST=None):
    """ """
    return self.sub_form.get_field(id)._render_helper(
        self.generate_subfield_key(id), value, REQUEST)

def render_sub_field_from_request(self, id, REQUEST):
    """ """
    return self.sub_form.get_field(id)._render_helper(
        self.generate_subfield_key(id), None, REQUEST)

def validate(self, REQUEST):
    """ """
    return self._validate_helper( self.generate_field_key(validation=1), REQUEST)
        
def validate_sub_field(self, id, REQUEST):
    """ """
    return self.sub_form.get_field(id)._validate_helper(
        self.generate_subfield_key(id, validation=1), REQUEST)
    
Field.field_record = None
Field.generate_field_key = generate_field_key
Field.generate_subfield_key = generate_subfield_key
Field.render = render
Field.render_from_request = render_from_request
Field.render_sub_field = render_sub_field
Field.render_sub_field_from_request = render_sub_field_from_request
Field.validate = validate
Field.validate_sub_field = validate_sub_field
