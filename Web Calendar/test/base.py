import requests
import datetime
from hstest import correct, WrongAnswer


def check_key_value_in_dict(dictionary, key, value=None):
    if key not in dictionary:
        raise WrongAnswer(f"Can't find '{key}' key in the response!")

    if not value:
        return

    if dictionary[key] != value:
        raise WrongAnswer(f"The '{key}' key value is wrong!\n"
                          f"Expected  : '{value}'\n"
                          f"Your value: '{dictionary[key]}'")


def check_status_code(response, correct_code, error_message):
    if response.status_code != correct_code:
        raise WrongAnswer(error_message)


def get_json_from_response(response):
    try:
        return response.json()
    except Exception:
        raise WrongAnswer("The server response should be in JSON format!")


def find_event(events, date, event_name):
    for event in events:
        check_key_value_in_dict(event, 'id')
        check_key_value_in_dict(event, 'date')
        check_key_value_in_dict(event, 'event')
        if event['date'] == date and event['event'] == event_name:
            return
    raise WrongAnswer("Can't find event with the following data:\n"
                      f"'event': {event_name}\n"
                      f"'date': {date}")


def check_today_events(events):
    today = datetime.date.today()

    for event in events:
        check_key_value_in_dict(event, 'date')
        if event['date'] != str(today):
            raise WrongAnswer("/event/today should return a list of today's events!\n"
                              "Found wrong event:\n"
                              f"{event}")


def test_get_request_on_first_stage(self):
    response = requests.get(self.get_url('/event/today'))
    data = get_json_from_response(response)

    check_key_value_in_dict(
        data, 'data',
        'There are no events for today!'
    )

    return correct()


def test_correct_request(self):
    tomorrow = str(datetime.date.today() + datetime.timedelta(days=1))

    response = requests.post(
        self.get_url('/event'),
        data={
            "event": "Video conference",
            "date": tomorrow
        }
    )

    check_status_code(
        response,
        200,
        "After making a correct POST request for '/event' URL the server should return HTTP status code 200"
    )

    data = get_json_from_response(response)

    check_key_value_in_dict(
        data, 'message',
        'The event has been added!'
    )

    check_key_value_in_dict(
        data, 'event',
        'Video conference'
    )

    check_key_value_in_dict(
        data, 'date',
        tomorrow
    )

    return correct()


def test_bad_request(self):
    response = requests.post(
        self.get_url('/event'),
        data={
            "date": str(datetime.datetime.now().date())
        }
    )

    data = get_json_from_response(response)

    check_key_value_in_dict(
        data, 'message'
    )

    check_key_value_in_dict(
        data['message'], 'event',
        'The event name is required!'
    )

    response = requests.post(
        self.get_url('/event'),
        data={
            "event": "Video conference",
        }
    )

    data = get_json_from_response(response)

    check_key_value_in_dict(
        data, 'message'
    )

    check_key_value_in_dict(
        data['message'], 'date',
        'The event date with the correct format is required! The correct format is YYYY-MM-DD!'
    )

    response = requests.post(
        self.get_url('/event'),
        data={
            "event": "Video conference",
            "date": '15-11-2020'
        }
    )

    data = get_json_from_response(response)

    check_key_value_in_dict(
        data, 'message'
    )

    check_key_value_in_dict(
        data['message'], 'date',
        'The event date with the correct format is required! The correct format is YYYY-MM-DD!'
    )

    return correct()


def test_get_events(self):
    requests.post(
        self.get_url('/event'),
        data={
            "event": "Today's first event",
            "date": str(datetime.date.today())
        }
    )

    requests.post(
        self.get_url('/event'),
        data={
            "event": "Today's second event",
            "date": str(datetime.date.today())
        }
    )

    requests.post(
        self.get_url('/event'),
        data={
            "event": "Tomorrow event",
            "date": str(datetime.date.today() + datetime.timedelta(days=1))
        }
    )

    response = requests.get(
        self.get_url('/event')
    )

    data = get_json_from_response(response)

    if type(data) != list:
        raise WrongAnswer("The response should be a list with events!")

    if len(data) < 3:
        raise WrongAnswer("The response list should contain at least 3 events!")

    find_event(data, str(datetime.date.today()), "Today's first event")
    find_event(data, str(datetime.date.today()), "Today's second event")

    return correct()


def test_today_events(self):
    response = requests.get(
        self.get_url('/event/today')
    )

    data = get_json_from_response(response)

    if type(data) != list:
        raise WrongAnswer("The response should be a list with events!")

    if len(data) < 2:
        raise WrongAnswer("The response list should contain at least 2 today's events!")

    check_today_events(data)

    return correct()


def check_events_in_range(self):
    requests.post(
        self.get_url('/event'),
        data={
            "event": "Event1",
            "date": str(datetime.date.today() + datetime.timedelta(days=10))
        }
    )

    requests.post(
        self.get_url('/event'),
        data={
            "event": "Event2",
            "date": str(datetime.date.today() + datetime.timedelta(days=15))
        }
    )

    requests.post(
        self.get_url('/event'),
        data={
            "event": "Event3",
            "date": str(datetime.date.today() + datetime.timedelta(days=20))
        }
    )

    response = requests.get(
        self.get_url('/event'),
        data={
            'time_start': str(datetime.date.today() + datetime.timedelta(days=9)),
            'time_end': str(datetime.date.today() + datetime.timedelta(days=11)),
        }
    )
    data = get_json_from_response(response)

    if type(data) != list:
        raise WrongAnswer("The response should be a list with events!")

    if len(data) != 1:
        raise WrongAnswer(
            f"Expected only one event in a range from {str(datetime.date.today() + datetime.timedelta(days=9))} "
            f"to {str(datetime.date.today() + datetime.timedelta(days=11))}")

    check_key_value_in_dict(
        data[0], 'event',
        'Event1'
    )

    response = requests.get(
        self.get_url('/event?'),
        data={
            'time_start': str(datetime.date.today() + datetime.timedelta(days=14)),
            'time_end': str(datetime.date.today() + datetime.timedelta(days=16)),
        }
    )

    data = get_json_from_response(response)

    if type(data) != list:
        raise WrongAnswer("The response should be a list with events!")

    if len(data) != 1:
        raise WrongAnswer(
            f"Expected only one event in a range from {str(datetime.date.today() + datetime.timedelta(days=14))} "
            f"to {str(datetime.date.today() + datetime.timedelta(days=16))}")

    check_key_value_in_dict(
        data[0], 'event',
        'Event2'
    )

    response = requests.get(
        self.get_url('/event'),
        data={
            'time_start': str(datetime.date.today() + datetime.timedelta(days=19)),
            'time_end': str(datetime.date.today() + datetime.timedelta(days=21)),
        }
    )

    data = get_json_from_response(response)

    if type(data) != list:
        raise WrongAnswer("The response should be a list with events!")

    if len(data) != 1:
        raise WrongAnswer(
            f"Expected only one event in a range from {str(datetime.date.today() + datetime.timedelta(days=19))} "
            f"to {str(datetime.date.today() + datetime.timedelta(days=21))}")

    check_key_value_in_dict(
        data[0], 'event',
        'Event3'
    )

    return correct()


def check_get_delete_by_id(self):
    response = requests.get(
        self.get_url('/event')
    )

    data = get_json_from_response(response)

    if type(data) != list:
        raise WrongAnswer("The response should be a list with events!")

    if len(data) == 0:
        raise WrongAnswer("Looks like you return an empty list of events!")

    event_id = data[-1]['id']

    response = requests.get(
        self.get_url(f'/event/{event_id}')
    )

    data = get_json_from_response(response)

    check_key_value_in_dict(
        data, 'id'
    )

    check_key_value_in_dict(
        data, 'event'
    )

    check_key_value_in_dict(
        data, 'date'
    )

    response = requests.delete(
        self.get_url(f'/event/{event_id}')
    )

    data = get_json_from_response(response)
    check_status_code(response, 200, 'After deleting an existing event you should response with status code 200!')

    check_key_value_in_dict(
        data, 'message',
        'The event has been deleted!'
    )

    response = requests.delete(
        self.get_url(f'/event/{event_id}')
    )

    data = get_json_from_response(response)
    check_status_code(
        response,
        404,
        "If the user tries to delete an event that doesn't exists you should response with status code 404!"
    )

    check_key_value_in_dict(
        data, 'message',
        "The event doesn't exist!"
    )

    response = requests.get(
        self.get_url(f'/event/{event_id}')
    )

    data = get_json_from_response(response)
    check_status_code(
        response,
        404,
        "If the user tries to delete an event that doesn't exists you should response with status code 404!"
    )

    check_key_value_in_dict(
        data, 'message',
        "The event doesn't exist!"
    )

    return correct()
