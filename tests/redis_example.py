import redis
import json

def run1():
    print('run1')
    client = redis.StrictRedis(host='127.0.0.1', port=6379)

    client.set("string:my_key", "Hello World")
    my_key = client.get("string:my_key")
    print('my_key:', my_key)
    # "Hello World"
    client.incr("string:counter")
    client.mget(["string:my_key", "string:counter"])
    # ['Hello World', '2']

    client.rpush("list:my_list", "item1", "item2")
    client.lpop("list:my_list")
    # 'item1'

    client.hset("set:redis_book", "title", "Redis Essentials")
    client.hgetall("set:redis_book")
    # {'title': 'Redis Essentials'}

    client.sadd("set:users", "alice", "bob")
    client.smembers("set:users") 
    # set(['bob', 'alice'])

    client.zadd("sorted_set:programmers", 1940, "Alan Kay")
    client.zadd("sorted_set:programmers", 1912, "Alan Turing")
    zvalues = client.zrange("sorted_set:programmers", 0, -1, withscores=True)
    print('zvalues:', zvalues)
    # [('Alan Turing', 1912.0), ('Alan Kay', 1940.0)]
    
    
def run2():
    print('run2')
    client = redis.StrictRedis(host='127.0.0.1', port=6379)

    kernel_info_input = {'execution_id': 'ex_1',
                'kernel_id': 'kid_1',
                'kernel_name': 'p2'}
                
    client.set('execution_id:ex_1', json.dumps(kernel_info_input))
    
    
    kernel_info_str = client.get('execution_id:ex_1')
    kernel_info = json.loads(kernel_info_str)
    print('kernel_info:', json.dumps(kernel_info, indent=4))
    
    kernel_info_input = {'execution_id': 'ex_2',
                'kernel_id': 'kid_2',
                'kernel_name': 'p2'}
                
    client.set('execution_id:ex_2', json.dumps(kernel_info_input))    
    
    keys = client.keys('execution_id:*')        
    print('keys:', keys)
    kernel_infos_strs = client.mget(keys)
    
    for kernel_infos_str in kernel_infos_strs:
        print('kernel_infos_str:', kernel_infos_str) 
        kernel_infos = json.loads(kernel_infos_str)
        print('kernel_infos:', json.dumps(kernel_infos, indent=4))

def run3():
    print('run3')
    client = redis.StrictRedis(host='localhost', port=6379)

    execution_id = 'execution-1'

    exec_hash = 'execution_id:' + execution_id

    venue_info = {'venue_id': 'venue-1',
        'venue_name': 'HK Venue'}

    variables = {'var1': 1.2, 'var2': 'abc'}

    # client.set('execution_id:' + execution_id, 'my execution')
    # get_str = client.get('execution_id:' + execution_id)
    # print('get_str:', get_str)    

    client.delete(exec_hash)
                
    # client.hset(exec_hash, 'venue_info', json.dumps(venue_info))
    # client.hset(exec_hash, 'last_step_status', 'SUCCESS')
    # client.hset(exec_hash, 'variables', json.dumps(variables))

    input_dict = {
        'venue_info': json.dumps(venue_info),
        'last_step_status': 'FAIL',
        'variables': json.dumps(variables)
    }

    client.hmset(exec_hash, input_dict)

    keys = client.hkeys(exec_hash)
    for key in keys:
        value_str = client.hget(exec_hash, key)
        print('key:', key, '   value_str:', value_str)

    for item in client.hscan_iter(exec_hash):
        print('item:', item)

    values = client.hmget(exec_hash, ['last_step_status', 'notakey'])    

    print('values:', values)


    client.delete(exec_hash)


def run4():
    print('run4')
    client = redis.StrictRedis(host='localhost', port=6379)

    execution_id = 'm2020-ingenium-10129'

    exec_hash = 'execution_id:' + execution_id


    for item in client.hscan_iter(exec_hash):
        print('item:', item)   
       
                  
if __name__ == '__main__':

    run4()
