import random

def getTemperature():
    return round(random.uniform(0, 40), 2)

def getUmidity():
    return round(random.uniform(0, 100), 2)

if __name__ == "__main__":
    print(getTemperature())
    print(getUmidity())