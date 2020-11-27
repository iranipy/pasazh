import secrets



def hex_generator():
    nums = list('0123456789ABCDEF')
    uid = str()
    while len(uid) < 8:
        uid += secrets.choice(nums)

    return uid



