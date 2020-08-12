from datetime import datetime
from flask import make_response, abort, jsonify
from flask_httpauth import HTTPBasicAuth
import json
import pusher
from dotenv import load_dotenv
import os
from gcloudenv import Settings
from random import choice, random
load_dotenv()

USERNAME = os.environ.get("API_USERNAME") or Settings.get("API_USERNAME")
PASSWORD = os.environ.get("API_PASSWORD") or Settings.get("API_PASSWORD")

def get_timestamp():
    return datetime.now().strftime(("%Y-%m-%d %H:%M:%S"))


auth = HTTPBasicAuth()


@auth.verify_password
def basic_auth(username, password):
    if username == USERNAME and password == PASSWORD:
        return True
    return False


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


@auth.login_required
def read():
    """
    Returns the entire starting roster
    """
    return WEEK


@auth.login_required
def update(weekday, time, assignee):
    """
    Takes the required shift (weekday and time) and updates who it is assigned to
    """
    updated_shift = {}
    for num, day in enumerate(WEEK):
        if weekday in day['day']:
            if time in WEEK[num]['shifts']:
                WEEK[num]['shifts'][time]['assignee'] = assignee
                WEEK[num]['shifts'][time]['timestamp'] = get_timestamp()
                add_to_pusher(WEEK)
                return make_response("", 204)

    return make_response("Shift not found", 404)


@auth.login_required
def unassigned_shifts():
    """
    Return all shifts where nobody is assigned
    """
    global WEEK
    no_worker = {'free_shifts': []}
    for num, days in enumerate(WEEK):
        for time, info in WEEK[num]['shifts'].items():
            if info['assignee'] is None:
                empty_shift = {}
                empty_shift['day'] = WEEK[num]['day']
                empty_shift['time'] = time
                no_worker['free_shifts'].append(empty_shift)
    return no_worker


def add_to_pusher(message):
    """
    Takes updates to the roster and sends it to Pusher for realtime dashboards to update
    """
    channels_client = pusher.Pusher(
        app_id=os.environ.get('PUSHER_APP_ID') or Settings.get('PUSHER_APP_ID'),
        key=os.environ.get('PUSHER_KEY') or Settings.get('PUSHER_KEY'),
        secret=os.environ.get('PUSHER_SECRET') or Settings.get('PUSHER_SECRET'),
        cluster='eu',
        ssl=True
    )

    channels_client.trigger('shifts', 'shift_updated', {'data': message})


def random_worker():
    """
    Picks a random worker with a chance of none to assign to a shift
    """
    names = ["Amal", "Eugena", "Kyra", "Harris", "Granville", "Brigette", "Daphine", "Erlinda", "Larae", "Claudia", "Chang", "Willian", "Reuben", "Neida", "Shonna", "Mimi", "Shannon", "Fallon", "Dannette", "Oren"]
    if random() < 0.25:
        return None
    else:
        return choice(names)


@auth.login_required
def reset_shifts():
    """
    Creates an all new roster. Helpful when the realtime display has no
    unassigned shifts left to show
    """
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
    add_to_pusher(WEEK)
    return make_response("New Roster Created and sent to Pusher", 201)
