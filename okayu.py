from file_mng import *

def okayu_up(list, key, value):
    list[key] = int(value)
    make_pkl(list, "okayu")

def okayu_num(list, key):
    return int(list[key])

def okayu_check(list, key):
    return key in list.keys()

def okayu_diff(list, key1, key2):
    result = ''
    if(okayu_num(list, key1) > okayu_num(list, key2)):
        result += f"WINNER {key1}"
    elif(okayu_num(list, key1) < okayu_num(list, key2)):
        result += f"WINNER {key2}"
    else:
        result += "DRAW"
    return result

def okayu_showall(list, key):
    yourscore = okayu_num(list, key)
    result = f"{key}({yourscore}草粥)VS\n"
    for k in list:
        if(key == k):
            continue
        result += f'    {k}({okayu_num(list, k)}草粥)\n        {okayu_diff(list, key, k)}\n'
    return result

def okayu_del(list, key):
    if okayu_check(list, key) == True:
        val = list.pop(key)
        make_pkl(list, "okayu")
        return val