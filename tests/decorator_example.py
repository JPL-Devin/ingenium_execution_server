from functools import wraps

def require_jwt(*expected_args):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print('expected_args:', expected_args)
            
            set_expected = set(expected_args)
            set_actual = set(args)
            
            if len(set_expected) > 0 and len(set_expected.intersection(set_actual)) == 0:
                raise Exception('Requirement not met')
                
            return func(*args, **kwargs)
        return wrapper
    return decorator

@require_jwt('admin', 'execution')
def test_jwt1(*args):
    print('test_jwt1:', args)

@require_jwt()
def test_jwt2(*args):
    print('test_jwt2:', args)
    
if __name__ == '__main__':
    test_jwt1('admin')
    
    test_jwt1('execution')

    test_jwt1('execution', 'admin')
    
    test_jwt2()    
    
    test_jwt2('admin')
    
    test_jwt1('jerry')
    
    
