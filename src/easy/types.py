_types = {}

class Type(object):
    def __init__(self, name):
        assert isinstance(name, str)
        assert (name not in _types), (name, _types)
        self.name = name 

    def __str__(self):
        return self.name

def get_or_create_type(type_name):
    if type_name is None:
        return None
    if type_name not in _types:
        _types[type_name] = Type(type_name)

    return _types[type_name]

Void = get_or_create_type('Void')
Number = get_or_create_type('Number')
String = get_or_create_type('String')
