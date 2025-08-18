import re
import uuid

def test_uuid():
    elem_id = uuid.uuid4()
    print(type(elem_id), elem_id)
    print(type(elem_id.hex), elem_id.hex)

def match_str(input_str):
    print('\ninput_str:', input_str)
    match_obj = re.match('/executions/([0-9a-zA-Z\-]+)/run', input_str)
    
    print(match_obj.group())
    
    groups = match_obj.groups()
    for idx, group in enumerate(groups):
        print(idx, group)
    
def main():
    match_str('/executions/defa-13da/run')
    match_str('/executions/defa-13Da/run')
    match_str('/executions/defa-13Da-Ad34-bdZ-1234/run')    
    match_str('/executions/defa13aa/run')
    match_str('/executions/defa13Aa/run')
    


if __name__ == '__main__':
    main()
