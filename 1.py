

def say_hello(func):
    def wrapper(*args, **kwargs):
        print("你好")
        return func(*args, **kwargs)
    return wrapper  # 去掉括号，返回wrapper函数对象

@say_hello
def add(x, y, z):    
    res = x + y + z
    return res

if __name__ == "__main__":
    result = add(x = 1, y = 2, z = 3)
    print(result)

