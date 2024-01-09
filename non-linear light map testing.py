import math as maths
e = maths.e
#print((maths.log(101)/9))

def exp(i):
    a = maths.log(101)/9
    return round(e**(0.51279*i) - 1)

def square(i):
    return round(i**2 * (100/81))

def inv_square(i):
    return round((i * (81/100))**(0.5))

def i_to(i):
    return round(i**(maths.log(100, 9)))

def dic_print(func, count=10):
    print("{", end="") 
    for i in range(count):
        print(str(i) + ":", end="")
        print(str(func(i)), end="")
        if i != count - 1:
            print(", ", end="")
    print("}")
    print("\n")

def just_print(func, count=10):
    for i in range(count):
        r = func(i)
        print(r, end=", ")
        print(inv_square(r))


dic_print(exp)
dic_print(square)
dic_print(i_to)
just_print(square)


