import datetime

def fun_greetings():
    now = datetime.datetime.now()
    hour = now.hour

    if hour < 12:
        greeting = "Good morning"
    elif hour < 15:
        greeting = "Good afternoon"
    elif hour < 20:
        greeting = "Good evening"
    else:
        greeting = "Good night"
    return greeting
    