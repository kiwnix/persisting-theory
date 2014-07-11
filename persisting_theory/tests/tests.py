import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import unittest 
import test_registries
import registries

registries.meta_registry.look_into = "test_registries"

TEST_APPS = (
    "app1",
    "app2",
)

class RegistryTest(unittest.TestCase):

    def test_can_infer_name_from_class_function_and_instance(self):
        registry = registries.Registry()

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
        registry = registries.Registry()
        registry.register(data, name="key")

        self.assertEqual(len(registry), 1)
        self.assertEqual(registry.get("key"), data)

    def test_can_restric_registered_data(self):

        class RestrictedRegistry(registries.Registry):
            def validate(self, obj):
                """Only accept integer values"""
                return isinstance(obj, int)

        registry = RestrictedRegistry()

        registry.register(12, name="twelve")
        with self.assertRaises(ValueError):
            registry.register("not an int", name="not an int")


    def test_can_register_class_and_function_via_decorator(self):
        registry = registries.Registry()

        @registry.register
        class ToRegister:
            pass

        self.assertEqual(registry.get('ToRegister'), ToRegister)

        @registry.register
        def something():
            pass

        self.assertEqual(registry.get('something'), something)
            
    def test_can_register_via_decorator_using_custom_name(self):
        registry = registries.Registry()

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

    def test_meta_registry_can_autodiscovering_registries_and_trigger_their_autodiscover_method(self):

        registry = registries.meta_registry
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


if __name__ == '__main__':
    unittest.main()