from datetime import datetime
from flask import make_response, abort, jsonify
import json
import pusher
from dotenv import load_dotenv
import os
from random import choice, random
load_dotenv()


def get_timestamp():
    return datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))


WEEK = [
    {
        "day": "Monday",
        "shifts": {
            "am": {
                "assignee": "Alice",
                "timestamp": get_timestamp()
            },
            "pm": {
                "assignee": None,
                "timestamp": get_timestamp()
            }
        }
    },
    {
        "day": "Tuesday",
        "shifts": {
            "am": {
                "assignee": "Stuart",
                "timestamp": get_timestamp()
            },
            "pm": {
                "assignee": "Bob",
                "timestamp": get_timestamp()
            }
        }
    },
    {
        "day": "Wednesday",
        "shifts": {
            "am": {
                "assignee": "Kimberly",
                "timestamp": get_timestamp()
            },
            "pm": {
                "assignee": None,
                "timestamp": get_timestamp()
            }
        }
    },
    {
        "day": "Thursday",
        "shifts": {
            "am": {
                "assignee": "Stuart",
                "timestamp": get_timestamp()
            },
            "pm": {
                "assignee": "Daisy",
                "timestamp": get_timestamp()
            }
        }
    },
    {
        "day": "Friday",
        "shifts": {
            "am": {
                "assignee": None,
                "timestamp": get_timestamp()
            },
            "pm": {
                "assignee": "Samantha",
                "timestamp": get_timestamp()
            }
        }
    },
    {
        "day": "Saturday",
        "shifts": {
            "am": {
                "assignee": "Natalie",
                "timestamp": get_timestamp()
            },
            "pm": {
                "assignee": "Buck",
                "timestamp": get_timestamp()
            }
        }
    },
    {
        "day": "Sunday",
        "shifts": {
            "am": {
                "assignee": "Brad",
                "timestamp": get_timestamp()
            },
            "pm": {
                "assignee": "Mitch",
                "timestamp": get_timestamp()
            }
        }
    }
]


def read():
    return WEEK


# def read_one(weekday, shift_time):
#     for num, day in enumerate(WEEK):
#         if weekday in day['day']:
#             for time in day['shifts']:
#                 if shift_time == time:
#                     shift = day['shifts'][time]
#     else:
#         abort(404, f"Shift {day} - {time} not found")

#     return shift


def update(weekday, time, assignee):
    for num, day in enumerate(WEEK):
        if weekday in day['day']:
            print("Found weekday", weekday)
            if time in WEEK[num]['shifts']:
                print("Found shidt time", time)
                WEEK[num]['shifts'][time]['assignee'] = assignee
                WEEK[num]['shifts'][time]['timestamp'] = get_timestamp()

                add_to_pusher(WEEK)
                return "OK", 200

    return "Shift not found"


def unassigned_shifts():
    global WEEK
    print(WEEK)
    no_worker = {'free_shifts': []}
    for num, days in enumerate(WEEK):
        for time, info in WEEK[num]['shifts'].items():
            if info['assignee'] is None:
                #day = {}
                #day['day'] = WEEK[num]['day']
                empty_shift = {}
                empty_shift['day'] = WEEK[num]['day']
                empty_shift['time'] = time
                #empty_shift['shift'][time] = info
                # day.update(empty_shift)

                #new_day = [WEEK[num]['day'], time]
                no_worker['free_shifts'].append(empty_shift)
    return no_worker


def add_to_pusher(message):
    channels_client = pusher.Pusher(
        app_id=os.environ.get('PUSHER_APP_ID'),
        key=os.environ.get('PUSHER_KEY'),
        secret=os.environ.get('PUSHER_SECRET'),
        cluster='eu',
        ssl=True
    )

    channels_client.trigger('shifts', 'shift_updated', {'data': message})


def random_worker():
    names = ["Amal", "Eugena", "Kyra", "Harris", "Granville", "Brigette", "Daphine", "Erlinda", "Larae", "Claudia", "Chang", "Willian", "Reuben", "Neida", "Shonna", "Mimi", "Shannon", "Fallon", "Dannette", "Oren"]
    if random() < 0.25:
        return None
    else:
        return choice(names)


def reset_shifts():
    global WEEK
    WEEK = []
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for day in days:
        shift = {}
        shift['day'] = day
        shifts = {
            'shifts': {
                'am': {
                    'assignee': random_worker(),
                    'timestamp': get_timestamp()
                },
                'pm': {
                    'assignee': random_worker(),
                    'timestamp': get_timestamp()
                }
            }
        }
        shift.update(shifts)
        WEEK.append(shift)
    print(WEEK)
    add_to_pusher(WEEK)
