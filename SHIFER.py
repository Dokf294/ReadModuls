import random
import string
import pyperclip

def random_char(y):
    return ''.join(random.choice(string.ascii_letters) for x in range(y))

def random_num():
    x = [1,2,3,4,5,6,7,8,9]
    sampling = random.choices(x, k=9)
    s = ''.join(map(str, sampling))
    y = random_char(5)+s
    b = ''.join(random.sample(y,len(y)))
    return b

def ENDCODE():
    num = random_char(5) + random_num()
    return num 
