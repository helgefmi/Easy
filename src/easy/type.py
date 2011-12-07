class Type(object):
    def __init__(self, name):
        self.name = name
    
    def __str__(self):
        return self.name

    def __eq__(self, other):
        return self.name == other.name
    
    def __ne__(self, other):
        return not (self == other)

    def change(self, new_name):
        if new_name != self.name and self.name != 'dunno':
            print 'Tried to change from %s to %s. No deal.' % (self.name, new_name)
            exit(1)
        self.name = new_name

    def known(self):
        return self.name != 'dunno'

    def incompatible(self, other):
        return not (self.name == 'dunno' or other.name == 'dunno' or self == other)
