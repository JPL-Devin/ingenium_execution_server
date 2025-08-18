from .ingenium_library import ing_profile

@ing_profile('DEBUG')
def my_func1(x1, x2):
    print 'inside my_func1'
    return x1+x2
    
@ing_profile('DEBUG')
def my_func2(x1, x2):
    print 'inside my_func2'
    
    return 2 * my_func1(x1, x2) 

if __name__ == '__main__':
    my_func2(2, 3)
    