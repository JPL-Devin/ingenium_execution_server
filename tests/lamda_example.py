import redis
import json


class MyClass(object):

    def __init__(self):
        self.mapping = dict()
        
    def add(self, key, value):
        self.mapping[key] = value
        
        def func():
            print(('remove key: {0} value: {1}'.format(key, value)))
            del self.mapping[key]
            
            print(('remaining keys: {0}'.format(list(self.mapping.keys()))))
            
        return func    
        
                  
if __name__ == '__main__':

    m = MyClass()
    
    f1 = m.add('one', '1')
    f2 = m.add('two', '2')

    f1()
    f2()    
