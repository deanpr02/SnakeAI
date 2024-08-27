def func1(a):
    print(f"This is function {a}")

def func2():
    print("This is function 2")

def main():
    dict1 = {
        "a": func1,
        "b": func2
    }
    dict1["a"](10)

main()