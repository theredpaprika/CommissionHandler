

class ProducerCleanerRegistry:
    registry = {}

    @classmethod
    def register(cls, name):
        def decorator(func):
            print("Registering {}".format(name))
            cls.registry[name] = func
            return func
        return decorator

    @classmethod
    def clean(cls, producer, file):
        if producer not in cls.registry:
            raise ValueError(f"Unsupported producer: {producer}")
        return cls.registry[producer](file)

# add decorator to each producer function, e.g:  @register_producer("SFG")