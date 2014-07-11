Introduction
============

Persisting-theory is a small python utility designed to automate data discovering and access inside a list of packages. Use case: you are building an application that will have pluggable components. You want to allow these components to register data so it can be accessed by any other component of your app.

Okay, I'm bad at explaining things, and english is not my mother. Let's build a simple example.

Quickstart
==========

A basic setup::

    # registries.py

    from persiting_theory import Registry

    class CallbacksRegistry(Registry):
        """
            Allow your apps to register callbacks
        """
        # the package where the registry will try to find callbacks in each app
        look_into = "callbacks_registry"

    callbacks_registry = CallbacksRegistry()


    # app1/callbacks_registry.py

    from registries import callbacks_registry

    @callbacks_registry.register
    def dog():
        print("Wouf")


    # app2/callbacks_registry.py

    from registries import callbacks_registry

    @callbacks_registry.register
    def cat():
        print("Meow")


    # dosomething.py

    from registries import callbacks_registry
    
    APPS = (
        'app1',
        'app2',
    )
    
    # Trigger autodiscovering process
    callbacks_registry.autodiscover(APPS)

    for callback in callbacks_registry.values():
        callback()

        # Wouf
        # Meow

API
===

``Registry`` inherits from python built-in `collections.OrderedDict`, which means you can use regular dict methods to access registered data::

    callbacks_registry.get("dog")()
    # Wouf

Registry.register
*****************

You can use this function as a decorator for functions and class::

    from persiting_theory import Registry

    class AwesomeRegistry(Registry):
        pass

    r = AwesomeRegistry()

    # register a class
    @r.register
    class AwesomeClass:
        pass

    # register a function
    @r.register
    def awesome_function():
        pass

    # By default, the key in the registry for a given value is obtained from the function or class name, if possible

    assert r.get("AwesomeClass") == AwesomeClass
    assert r.get("awesome_function") == awesome_function

    # You can override this behaviour:

    @r.register(name="Chuck")
    class AwesomeClass:
        pass

    @r.register(name="Norris")
    def awesome_function():
        pass

    assert r.get("Chuck") == AwesomeClass
    assert r.get("Norris") == awesome_function


    # You can also use the register method as is

    awesome_var = "Chuck Norris"
    r.register(awesome_var, name="Who am I ?")

    assert r.get("Who am I ?") == awesome_var

    # I f you are not registering a function or a class, you MUST provide a name argument

Registry.validate
*****************

By default, a registry will accept any value registered. Sometimes, it's not what you want, so you can restric what kind of data you accept::

    from persiting_theory import Registry

    class StartsWithAwesomeRegistry(Registry):

        def validate(self, obj):
            if isinstance(obj, str):
                return obj.startswith("awesome")
            return False

    r = AwesomeRegistry()

    # will pass registration
    r.register("awesome day", name="awesome_day")

    # will fail and raise ValueError
    r.register("not so awesome day", name="not_so_awesome_day")

Going meta
**********

If you have multiple registries, or want to allow your apps to declare their own registries, this is for you::

    # registries.py

    from persisting_theory import meta_registry, Registry


    class RegistryA(Registry)
        look_into = "a"
    
    class RegistryB(Registry)
        look_into = "b"

    registry_a = RegistryA()
    meta_registry.register(registry_a, name="registry_a")

    registry_b = RegistryB()
    meta_registry.register(registry_b, name="registry_b")


    # dosomethingelse.py

    from persisting_theory import meta_registry

    # will import registries declared in `registries` packages, and trigger autodiscover() on each of them
    meta_registry.autodiscover(apps=("app1", "app2"))


What the hell is that name ?
============================

It's an anagram for "python registries". 

Contribute
==========

Contributions, bug reports, and thank you are welcomed. Feel free to contact me at <contact@eliotberriot.com>.

License
=======

The project is licensed under BSD licence.