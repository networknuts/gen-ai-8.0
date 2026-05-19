def first_func():
    print("hello anil")
    print("hello chandrasekhar")
    print("hello python")

def second_func():
    print("hello aryan")

def say_hello(user="john"):
    print(f"hello {user}")

def add_together(x,y):
    return(x+y)

result = add_together(5,5)

def create_user_profile(username,userid):
    return {
        "USER": username,
        "ID": userid
    }

result = create_user_profile("chandrasekhar",101)
print(result)