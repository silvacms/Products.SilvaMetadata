"""
Tests for the SilvaMetada.

$Id: test_Metadata.py,v 1.21 2005/09/14 22:30:53 clemens Exp $
"""

from unittest import TestSuite, makeSuite, main

from cStringIO import StringIO

from Testing import ZopeTestCase

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from Products.Annotations.AnnotationTool import AnnotationTool

from Products.Formulator import StandardFields
from Products.Formulator.TALESField import TALESMethod
from Products.SilvaMetadata.MetadataTool import MetadataTool
from Products.SilvaMetadata.Compatibility import getToolByName
from Products.SilvaMetadata.Configuration import UsingCMF

if UsingCMF:
    from Products.CMFCore.CatalogTool import CatalogTool
    from Products.CMFCore.PortalFolder import PortalFolder
    from Products.CMFCore.tests.base.testcase import SecurityTest
    from Products.CMFCore.TypesTool import FactoryTypeInformation as FTI
    from Products.CMFCore.TypesTool import TypesTool
    from Products.CMFCore.utils import getToolByName

    ZopeTestCase.installProduct('Annotations')
    ZopeTestCase.installProduct('ProxyIndex')
    ZopeTestCase.installProduct('Formulator')
    ZopeTestCase.installProduct('CMFCore')
    # needed by more recent cmf, at east since 1.5.4
    ZopeTestCase.installProduct('ZCTextIndex')
    TestBaseClass = ZopeTestCase.ZopeTestCase
else:
    from Products.Silva.tests import SilvaTestCase
    TestBaseClass = SilvaTestCase.SilvaTestCase

SET_ID = 'ut_md'


def setupFakePermissions(root):
    # copy & paste from ZopeTestCase :-/
    uf = root.acl_users
    uf.userFolderAddUser( '_test_user', 'secret', ['Manager'], [])
    user = uf.getUserById('_test_user').__of__(uf)
    newSecurityManager(None, user)

def setupCMFTools(root):
    root._setObject('portal_types', TypesTool())
    root._setObject('portal_annotations', AnnotationTool())
    root._setObject('portal_metadata', MetadataTool())
    root._setObject('portal_catalog', CatalogTool())

def setupContentTypes(context):
    types_tool = getToolByName(context, 'portal_types')
    types_tool._setObject('Folder', FTI(id='Folder',
                                        title='Folder or Directory',
                                        meta_type=PortalFolder.meta_type,
                                        product='CMFCore',
                                        factory='manage_addPortalFolder',
                                        filter_content_types=0)
                             )

def setupContentTreeCMF(container):
    ttool = getToolByName(container, 'portal_types')
    ttool.constructContent('Folder', container, 'zoo')

    zoo = container._getOb('zoo')

    ttool.constructContent('Folder', zoo, 'mammals')
    ttool.constructContent('Folder', zoo, 'reptiles')

    mammals = zoo._getOb('mammals')
    reptiles = zoo._getOb('reptiles')

    return zoo

def setupContentTreeSilva(self, container):

    zoo = self.add_folder(container, 'zoo', "Zoo Folder")
    self.add_folder(zoo, 'mammals', "Zoo Mammals")
    zoo = self.add_folder(zoo, 'reptiles', "Zoo Reptiles")
    return zoo

def setupCatalog(context):
    catalog = getToolByName(context, 'portal_catalog')
    pass

def setupMetadataSet(context):
    mtool = getToolByName(context, 'portal_metadata')
    collection = mtool.getCollection()
    collection.addMetadataSet(SET_ID,
                              'tmd',
                              'http://www.example.com/xml/test_md')
    set = collection.getMetadataSet(SET_ID)
    set.addMetadataElement('Title',
                           StandardFields.StringField.meta_type,
                           'KeywordIndex',
                           1
                           )
    set.addMetadataElement('Description',
                           StandardFields.StringField.meta_type,
                           'KeywordIndex',
                           1
                           )
    element = set.getElement('Description')
    element.field._edit({'required':0})
    element.editElementPolicy(acquire_p = 1)
    return set

def setupExtendedMetadataSet(context):
    # add some additional metadata fields
    pm = getToolByName(context, 'portal_metadata')
    collection = pm.getCollection()
    set = collection.getMetadataSet(SET_ID)
    set.addMetadataElement('ModificationDate',
                           StandardFields.DateTimeField.meta_type,
                           'DateIndex',
                           1
                           )
    element = set.getElement('ModificationDate')
    element.field._edit_tales({'default':
                        TALESMethod('content/bobobase_modification_time')})
    element.field._edit({'required':0})
    set.addMetadataElement('Languages',
                           StandardFields.LinesField.meta_type,
                           'KeywordIndex',
                           1
                           )
    element = set.getElement('Languages')
    element.field._edit({'required':0})
    ######
    set.initialize()

def setupMetadataMapping(context):
    mtool = getToolByName(context, 'portal_metadata')
    mapping = mtool.getTypeMapping()
    mapping.setDefaultChain('ut_md')
    if not UsingCMF:
        mtool.addTypesMapping(
            ('Silva Folder', ), ('ut_md', 'silva-extra'))


class MetadataTests(TestBaseClass):

    def afterSetUp(self):
        if UsingCMF:
            self.root = self.app
            setupFakePermissions(self.root)
            setupCMFTools(self.root)
            setupCatalog(self.root)
            setupContentTypes(self.root)

        setupMetadataSet(self.root)
        setupMetadataMapping(self.root)
        if UsingCMF:
            setupContentTreeCMF(self.root)
        else:
            setupContentTreeSilva(self, self.root)


class TestSetImportExport(MetadataTests):

    def testImportExport(self):
        pm = getToolByName(self.root, 'portal_metadata')
        collection = pm.getCollection()
        set = collection.getMetadataSet(SET_ID)
        xml = set.exportXML().encode('ascii')
        xmlio = StringIO(xml)
        collection.manage_delObjects([SET_ID])
        collection.importSet(xmlio)
        set = collection.getMetadataSet(SET_ID)
        xml2 = set.exportXML()
        assert xml == xml2, "Import/Export disjoint"


class TestObjectImportExport(MetadataTests):

    def testImportExport(self):
        from Products.ParsedXML.ParsedXML import createDOMDocument
        from Products.SilvaMetadata.Import import import_metadata

        pm = getToolByName(self.root, 'portal_metadata')
        setupExtendedMetadataSet(self.root)
        zoo = self.root.zoo
        mammals = zoo.mammals
        binding = pm.getMetadata(zoo)
        values = binding.get(SET_ID)
        lines = """
        english
        hebrew
        swahili
        urdu
        """
        values.update(
            {'Title':'hello world',
             'Description':'cruel place',
             'Languages':lines }
            )
        binding.setValues(SET_ID, values)
        xml = "<folder>%s</folder>" % binding.renderXML(SET_ID)
        dom = createDOMDocument(xml)
        import_metadata(mammals, dom.childNodes[0])
        mammals_binding = pm.getMetadata(mammals)
        mammal_values = binding.get(SET_ID)
        for k in values.keys():
            self.assertEqual(values[k], mammal_values[k],
                             "Object Import/Export disjoint")

        xml2 = "<folder>%s</folder>" % mammals_binding.renderXML(SET_ID)
        xml_list = xml.splitlines()
        xml2_list = xml2.splitlines()
        for x in xml2_list:
            self.assert_(x in xml_list, "Object Import Export disjoin")
        for x in xml_list:
            self.assert_(x in xml2_list, "Object Import Export disjoin")


class TestCataloging(MetadataTests):
    pass


class TestMetadataElement(MetadataTests):

    def testGetDefault(self):
        pm = getToolByName(self.root, 'portal_metadata')
        collection = pm.getCollection()
        set = collection.getMetadataSet(SET_ID)
        element = set.getElement('Title')
        element.field._edit_tales({'default':
                                   TALESMethod('content/getPhysicalPath')})
        zoo = self.root.zoo
        binding = pm.getMetadata(zoo)
        defaults = set.getDefaults(content = zoo)
        self.assertEqual(defaults['Title'],
                         zoo.getPhysicalPath(),
                         "Tales Context Passing Failed")

    def testGetDefaultWithTalesDelegate(self):
        mtool = getToolByName(self.root, 'portal_metadata')
        mtoolId = mtool.getId()
        collection = mtool.getCollection()
        set = collection.getMetadataSet(SET_ID)
        zoo = self.root.zoo
        test_value = 'Rabbits4Ever'
        binding = mtool.getMetadata(zoo)
        binding.setValues(SET_ID, {'Title':test_value})
        element = set.getElement('Description')
        # yikes, narly tales expression
        method = "python: content.%s.getMetadata(content).get(" \
                 "'%s', 'Title', no_defaults=1)" % (mtoolId, SET_ID)
        element.field._edit_tales({'default': TALESMethod(method)})
        value = binding.get(SET_ID, 'Description')
        self.assertEqual(value, test_value,
                         "Tales delegate for default didn't work")
        # make sure the right cached value was stored.
        value = binding.get(SET_ID, 'Description')
        self.assertEqual(value, test_value, "Wrong Data Object Cached")
        # test shortcut, too
        self.assertEqual(value,
                         mtool.getMetadataValue(zoo, SET_ID, 'Description'))

    def testAcquisitionInvariant(self):
        # invariant == can't be required and acquired
        from Products.SilvaMetadata.Exceptions import ConfigurationError
        pm = getToolByName(self.root, 'portal_metadata')
        collection = pm.getCollection()
        set = collection.getMetadataSet(SET_ID)
        element = set.getElement('Description')
        try:
            element.field._edit({'required':1})
            element.editElementPolicy(acquire_p = 1)
        except ConfigurationError:
            pass
        else:
            raise AssertionError("Acquisition/Required Element" \
                                 " Invariant Failed")
        try:
            element.field._edit({'required':0})
            element.editElementPolicy(acquire_p = 1)
            element.field._edit({'required':1})
        except ConfigurationError:
            pass
        else:
            raise AssertionError("Acquisition/Required Element" \
                                 " Invariant Failed 2")


class TestAdvancedMetadata(MetadataTests):
    """Tests for runtime binding methods"""

    def setupAcquiredMetadata(self):
        zoo = self.root.zoo
        binding = getToolByName(zoo, 'portal_metadata').getMetadata(zoo)
        set_id = SET_ID
        binding.setValues(set_id, {'Title':'hello world',
                                   'Description':'cruel place'})

    def testContainmentAcquisitionValue(self):
        self.setupAcquiredMetadata()
        zoo = self.root.zoo
        mams = zoo.mammals
        z_binding = getToolByName(zoo, 'portal_metadata').getMetadata(zoo)
        m_binding = getToolByName(mams, 'portal_metadata').getMetadata(mams)
        set_id = SET_ID
        self.assertEqual(m_binding[set_id]['Description'],
                         z_binding[set_id]['Description'])
        # test shortcut, too
        self.assertEqual(getToolByName(mams, 'portal_metadata').getMetadataValue(mams,set_id,'Description'),
                         getToolByName(zoo, 'portal_metadata').getMetadataValue(zoo,set_id,'Description'))
        self.assertNotEqual(m_binding.get(set_id, 'Description', acquire=0),
                            z_binding[set_id]['Description'])

    def testContainmentAcquisitionList(self):
        self.setupAcquiredMetadata()
        zoo = self.root.zoo
        mams = zoo.mammals
        m_binding = getToolByName(mams, 'portal_metadata').getMetadata(mams)
        z_binding = getToolByName(zoo, 'portal_metadata').getMetadata(zoo)
        set_id = SET_ID
        acquired = m_binding.listAcquired()
        # test the contained's list acquired
        self.assertEqual(len(acquired), 1)
        self.assertEqual(acquired[0][1], 'Description')
        # test the container's listacquired
        acquired = z_binding.listAcquired()
        self.assertEqual(len(acquired), 0)
        # special case for
        z_binding.setValues(set_id, {'Title':'', 'Description':''})
        acquired = z_binding.listAcquired()
        self.assertEqual(len(acquired), 0)

    def testObjectDelegation(self):
        from Acquisition import Implicit
        class Delegator(Implicit):
            def __init__(self, name):
                self.name = name
            def __call__(self):
                ob = self.aq_inner.aq_parent
                return getattr(ob, self.name)

        zoo = self.root.zoo
        delegate = Delegator('reptiles')
        zoo.delegate = delegate
        mams = zoo.mammals
        reps = zoo.reptiles
        r_binding = getToolByName(reps, 'portal_metadata').getMetadata(reps)
        m_binding = getToolByName(mams, 'portal_metadata').getMetadata(mams)
        r_binding.setValues(SET_ID,
                            {'Title':'snake food',
                             'Description':'yummy n the tummy'}
                            )
        m_binding.setObjectDelegator('delegate')
        self.assertEqual(
            m_binding[SET_ID]['Title'],
            r_binding[SET_ID]['Title']
            )
        # test shortcut, too
        self.assertEqual('snake food',
                         getToolByName(mams, 'portal_metadata').
                              getMetadataValue(mams, SET_ID, 'Title'))        
        m_binding.clearObjectDelegator()
        assert m_binding[SET_ID]['Title'] != r_binding[SET_ID]['Title']

    def testMutationTriggerDelegation(self):
        class MutationTrigger:
            def __init__(self):
                self.called = 0
            def __call__(self):
                self.called += 1

        zoo = self.root.zoo
        mams = zoo.mammals
        m_binding = getToolByName(mams, 'portal_metadata').getMetadata(mams)
        trigger = MutationTrigger()
        zoo.trigger = trigger
        m_binding.setMutationTrigger(SET_ID, 'Title', 'trigger')
        m_binding.setValues(SET_ID, {'Title':'surfin betty',
                                     'Description':'morning pizza'})
        self.assertEqual(trigger.called, 1)
        m_binding.setValues(SET_ID, {'Description':'midnight raid'})
        self.assertEqual(trigger.called, 1)
        m_binding.clearMutationTrigger(SET_ID)
        # props to tennyson
        m_binding.setValues(SET_ID,
                            {'Title':
                             'To strive, to seek, to find, and not to yield'}
                            )
        self.assertEqual(trigger.called, 1)


def test_suite():
    suite = TestSuite()
    suite.addTest(makeSuite(TestSetImportExport))
    suite.addTest(makeSuite(TestObjectImportExport))
    suite.addTest(makeSuite(TestCataloging))
    suite.addTest(makeSuite(TestMetadataElement))
    suite.addTest(makeSuite(TestAdvancedMetadata))
    return suite


if __name__ == '__main__':
    main()

