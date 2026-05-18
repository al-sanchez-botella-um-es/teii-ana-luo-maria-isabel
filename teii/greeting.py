# greeting.py
def greeting(name: str) -> str:
    return f"Hello {name}"

def farewell(name):
    return f"Bye {name}"

greeting("Bob")
greeting(b'Alice')
greeting(3)

farewell("Bob")
farewell(b'Alice')
farewell(3)