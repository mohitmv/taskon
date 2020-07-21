import time

def makeSandwitch(bread, onion, grill_duration):
    print("Cutting " + onion)
    print("Grilling " + bread + " for " + str(grill_duration)+ " minutes")
    return onion + "-Sandwitch"

def makeBread(flour):
    print("Processing " + flour)
    return "Bread"

def buyOnion():
    return "Onion"

def makeFaultyBread(flour):
    # Raising exception deliberately.
    # This bread making task should fail.
    1/0

def buyCheese():
    return "Cheese"

def makeCheeseSandwitch(bread, cheese, onion, grill_duration):
    print("Cutting " + onion)
    print("Grilling " + bread + " for " + str(grill_duration)+ " minutes")
    return onion + "-" + cheese + "-Sandwitch"

def makeFaultyBreadSleep1(flour):
    time.sleep(1)
    # Raising exception deliberately.
    # This bread making task should fail after consuming 1 second.
    1/0;

def buyOnionSleep2():
    time.sleep(2)
    return "Onion"

def makeMoney(sandwitch):
    print("Selling sandwitch to make money")
    return "Money"

def buyGoodOnion(money):
    print("Buying onions of good quality")
    return "Onion"
