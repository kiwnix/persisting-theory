
import unittest 
from . import test_registries
import persisting_theory

persisting_theory.meta_registry.look_into = "test_registries"

TEST_APPS = (
    "tests.app1",
    "tests.app2",
)

class RegistryTest(unittest.TestCase):

    def test_can_infer_name_from_class_function_and_instance(self):
        registry = persisting_theory.Registry()

        def something():
            pass

        class MyClass:
            pass

        self.assertEqual(registry.get_object_name(something), "something")
        self.assertEqual(registry.get_object_name(MyClass), "MyClass")

        with self.assertRaises(ValueError):
            self.assertEqual(registry.get_object_name(MyClass()), "MyClass")

    def test_can_register_data_to_registry(self):

        data = "something"
        registry = persisting_theory.Registry()
        registry.register(data, name="key")

        self.assertEqual(len(registry), 1)
        self.assertEqual(registry.get("key"), data)

    def test_can_restric_registered_data(self):

        class RestrictedRegistry(persisting_theory.Registry):
            def validate(self, obj):
                """Only accept integer values"""
                return isinstance(obj, int)

        registry = RestrictedRegistry()

        registry.register(12, name="twelve")
        with self.assertRaises(ValueError):
            registry.register("not an int", name="not an int")


    def test_can_register_class_and_function_via_decorator(self):
        registry = persisting_theory.Registry()

        @registry.register
        class ToRegister:
            pass

        self.assertEqual(registry.get('ToRegister'), ToRegister)

        @registry.register
        def something():
            pass

        self.assertEqual(registry.get('something'), something)
            
    def test_can_register_via_decorator_using_custom_name(self):
        registry = persisting_theory.Registry()

        @registry.register(name="custom_name")
        def something():
            pass

        self.assertEqual(registry.get('custom_name'), something)

    def test_registry_can_autodiscover(self):

        registry = test_registries.awesome_people
        registry.autodiscover(apps=TEST_APPS)

        self.assertEqual(len(registry), 2)
        self.assertNotEqual(registry.get('AlainDamasio', None), None)
        self.assertNotEqual(registry.get('FrederikPeeters', None), None)

        registry.clear()

    def test_autodiscover_raises_an_error_if_there_is_an_error_in_imported_module(self):
        with self.assertRaises(NameError):
            registry = test_registries.awesome_people
            registry.autodiscover(apps=('tests.buggy_app',))

    def test_meta_registry_can_autodiscovering_registries_and_trigger_their_autodiscover_method(self):

        registry = persisting_theory.meta_registry
        registry.autodiscover(apps=TEST_APPS)

        self.assertEqual(len(registry), 2)
        self.assertEqual(registry.get('awesome_people'), test_registries.awesome_people)
        self.assertEqual(registry.get('vegetable_registry'), test_registries.vegetable_registry)

        registry = test_registries.awesome_people
        self.assertEqual(len(registry), 2)
        self.assertNotEqual(registry.get('AlainDamasio', None), None)
        self.assertNotEqual(registry.get('FrederikPeeters', None), None)

        registry = test_registries.vegetable_registry
        self.assertEqual(len(registry), 2)
        self.assertNotEqual(registry.get('Potato', None), None)
        self.assertNotEqual(registry.get('Ketchup', None), None)

    def test_can_manipulate_data_before_registering(self):

        class ModifyData(persisting_theory.Registry):
            def prepare_data(self, data):
                return "hello " + data

        r = ModifyData()

        r.register("eliot", name="eliot")
        r.register("roger", name="roger")

        self.assertEqual(r.get('eliot'), "hello eliot")
        self.assertEqual(r.get('roger'), "hello roger")

    def test_can_manipulate_key_before_registering(self):

        class ModifyKey(persisting_theory.Registry):
            def prepare_name(self, data, key=None):
                return "custom_key " + data.first_name

        r = ModifyKey()

        class N:
            def __init__(self, first_name):
                self.first_name = first_name

        n1 = N(first_name="eliot")
        n2 = N(first_name="alain")
        r.register(n1)
        r.register(n2)

        self.assertEqual(r.get('custom_key eliot'), n1)
        self.assertEqual(r.get('custom_key alain'), n2)

    def test_can_post_register_triggers_correctly(self):

        class PostRegisterException(Exception):
            pass

        class PostRegister(persisting_theory.Registry):
            def post_register(self, data, name):
                raise PostRegisterException('Post register triggered')

        r = PostRegister()        

        with self.assertRaises(PostRegisterException):
            r.register("hello", name="world")


if __name__ == '__main__':
    unittest.main()