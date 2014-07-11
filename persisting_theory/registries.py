from collections import OrderedDict
import inspect

class Registry(OrderedDict):

    def register_decorator_factory(self, **kwargs):
        """ 
            Return an actual decorator for registering objects into registry
        """ 
        name = kwargs.get('name')
        def decorator(decorated):
            self.register_func(obj=decorated, name=name)
            return decorated
        return decorator

    def register(self, obj=None, name=None, **kwargs):
        """
            Use this method as a decorator on class/funciton you want to register:

            @registry.register(name="test")
            class Test:
                pass

            :param:obj: An object to register in the registry
            :param:name: The name of the object to register. If none, the obj class name will be used


        """
        if obj is None:
            return self.register_decorator_factory(obj=obj, name=name, **kwargs)
        else:
            self.register_func(obj=obj, name=name, **kwargs)
            return obj

    def get_object_name(self, obj):
        """
            Return a name from an element (object, class, function...)
        """
        if callable(obj):
            return obj.__name__

        elif inspect.isclass(obj):
            return obj.__class__.__name__

        else:
            raise ValueError("Cannot deduce name from given object ({0}). Please user registry.register() with a 'name' argument.".format(obj))

    def validate(self, obj):
        """
            Called before registering a new value into the registry
            Override this method if you want to restrict what type of data cna be registered
        """
        return True

    def register_func(self, obj, name=None, **kwargs):
        """
            Register an object, class, function... into the registry
        """
        if self.validate(obj):
            if name is None:
                name = self.get_object_name(obj)
            self[name] = obj
        else:
            raise ValueError("{0} (type: {0.__class__}) is not a valid value for {1} registry".format(obj, self.__class__))

    def autodiscover(self, apps, force_reload=True):
        """
            Iterate throught every installed apps, trying to import `look_into` package
            :param apps: an iterable of string, refering to python modules the registry will try to import via autodiscover
        """
        for app in apps:
            try:
                package = '{0}.{1}'.format(app, self.look_into) # try to import self.package inside current app
                #print(package)
                module = __import__(package)
                if force_reload:
                    reload(module)
            except ImportError, e:
                # Module does not exist 
                pass


class MetaRegistry(Registry):
    """
        Keep a reference to all registries
    """
    look_into = "registries"

    def autodiscover(self, apps, cascade=True, **kwargs):
        """
            :param cascade: If true, will trigger autodiscover on discovered registries
        """
        super(MetaRegistry, self).autodiscover(apps, **kwargs)
        if cascade:
            self.autodiscover_registries(apps)

    def autodiscover_registries(self, apps):
        for key, registry in self.iteritems():
            registry.autodiscover(apps)
            
meta_registry = MetaRegistry()