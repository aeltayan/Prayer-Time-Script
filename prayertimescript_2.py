import datetime
import time
from copy import deepcopy

import requests
from plyer import notification
from requests import RequestException

base_url = "http://api.aladhan.com/v1/timingsByAddress/:date"
params = {
    'address': 'Your Address',
    'method': 1
}


def make_api_request(target_url: str, request_params: dict):
    """
    Makes a http request to the api. The request is returned as long
    as a network error does not occur. If a network error occurs the programs
    tries to make the request again for a max of three attempts. If max attempts
    are reached the program terminates.
    """

    max_attempts = 3

    while max_attempts > 0:

        try:

            request = requests.get(target_url, request_params)

            return request

        except RequestException:

            network_error_notification()
            max_attempts -= 1
            time.sleep(30)

    print('Max retry attempts... terminating program.')
    exit(0)


def handle_api_request_response(api_request) -> dict:
    """
    This function handles some very basic status code return, any code other than 200 will
    simply terminate the program as I honestly don't know how to handle status codes other
    than 200. Program exits with status code 1 to indicate an error has occurred.
    """

    if api_request.status_code == 200:  # Good Response
        prayer_times = obtain_prayer_times(api_request)
        return prayer_times

    if api_request.status_code == 400:  # Bad response
        status_code_notification(api_request.status_code)
        exit(1)

    if api_request.status_code == 500:  # Internal server error
        status_code_notification(api_request.status_code)
        exit(1)

    else:
        status_code_notification(api_request.status_code)
        exit(1)


def network_error_notification():

    notification_title = 'Network Error'
    notification_message = 'Connect to the internet...retrying in thirty seconds.'
    notification.notify(
        title = notification_title,
        message = notification_message,
        timeout = 10
    )


def status_code_notification(status_code: int):

    if status_code == 400:
        notification_title = 'Bad Request (400)'
        notification_message = 'Exiting program.'
        notification.notify(
            title = notification_title,
            message = notification_message,
            timeout = 10
        )

    if status_code == 500:
        notification_title = 'Internal Server Error (500)'
        notification_message = 'Exiting program.'
        notification.notify(
            title = notification_title,
            message = notification_message,
            timeout = 10
        )

    else:
        notification_title = f'Unknown Status Code {status_code}'
        notification_message = 'Exiting program.'
        notification.notify(
            title = notification_title,
            message = notification_message,
            timeout = 10
        )

def prayer_notification(prayer:str):

    notification.notify(
        title=f'{prayer} Adhan',
        message=f'It is now {prayer} time.',
        timeout = 10
    )


def obtain_prayer_times(api_request) -> dict:
    """
    Convert our request information into JSON format as the API I am making the request too
    allows for easy conversion into JSON format.
    """

    request_data = api_request.json()

    prayer_times = request_data['data']['timings']

    return prayer_times


def get_current_time() -> int:
    """
    Gets current time using datetime module and then formats the time into HHMM format
    to allow for easy calculations with the obtained prayer times which are in a 24-hour
    military time format.
    """

    current_time = str(datetime.datetime.now().time())

    time_formatted = int(current_time[:5].replace(':', ''))  # Turns time into HHMM format

    return time_formatted


def format_prayer_times(prayer_times: dict) -> dict:
    """
    Takes all the timings within the prayer times dictionary and converts them
    to int type, removes the colon and adds them back to the prayer times dictionary
    to allow them to be used in mathematical operations when trying to find the time difference.
    A deepcopy of the original dict in order to prevent any complications with the original dict as
    we are deleting and changing values.
    """

    prayer_times_copy = deepcopy(prayer_times)

    del prayer_times_copy['Lastthird']
    del prayer_times_copy['Firstthird']
    del prayer_times_copy['Midnight']
    del prayer_times_copy['Imsak']
    del prayer_times_copy['Sunset']

    for prayer, times in prayer_times_copy.items():
        prayer_times_copy[prayer] = int(times.replace(':', ''))


    return prayer_times_copy


def check_for_next_prayer(prayer_times: dict, current_time: int):

    if current_time > prayer_times['Isha']:
        wait_till_midnight = time_till_midnight(current_time)
        time.sleep(wait_till_midnight)
        pass

    elif  current_time < prayer_times['Fajr']:
        time_difference = find_time_difference(prayer_times['Fajr'], current_time)
        check_if_prayer_time('Fajr', time_difference)

    elif current_time < prayer_times['Sunrise']:
        time_difference = find_time_difference(prayer_times['Sunrise'], current_time)
        check_if_prayer_time('Sunrise', time_difference)

    elif current_time < prayer_times['Dhuhr']:
        time_difference = find_time_difference(prayer_times['Dhuhr'], current_time)
        check_if_prayer_time('Dhuhr', time_difference)

    elif current_time < prayer_times['Asr']:
        time_difference = find_time_difference(prayer_times['Asr'], current_time)
        check_if_prayer_time('Asr', time_difference)

    elif current_time < prayer_times['Maghrib']:
        time_difference = find_time_difference(prayer_times['Maghrib'], current_time)
        check_if_prayer_time('Maghrib', time_difference)

    elif current_time < prayer_times['Isha']:
        time_difference = find_time_difference(prayer_times['Isha'],current_time)
        check_if_prayer_time('Isha', time_difference)


def time_till_midnight(current_time: int) -> int:

    wait_till_midnight = 2400 - current_time

    wait_till_midnight = find_time_until_prayer(wait_till_midnight)

    return wait_till_midnight


def find_time_difference(prayer_time: int, current_time: int) -> int:
    """
    Finds the time difference between the next prayer and the current time. Since we are
    trying to find the time difference we have to take into account that when the difference
    between our two integers exceeds 60 we are not able to represent that difference as a
    'time' difference. For example: 80 is the difference be 1400, 1320. 1400 is 2 o clock
    and 1320 is 1:20 o clock, so we subtract 40 to get the actual time difference between the two
    which is 40 minutes
    """

    time_deference = prayer_time - current_time

    if time_deference > 60:

        time_difference = time_deference - 40

        return time_difference

    else:

        return time_deference



def find_time_until_prayer(time_difference: int) -> int:
    """
    This function finds the amount of time until the Adhaan in seconds.
    """

    if time_difference >= 100:

        hours = int(str(time_difference)[0:1])

        minutes = int(str(time_difference)[1:])

        time_in_seconds = (hours * 3600) + (minutes * 60)

        return time_in_seconds

    else:

        time_in_seconds = time_difference * 60

        return time_in_seconds


def check_if_prayer_time(prayer: str, time_difference: int):
    """
    The time until prayer variable is the amount of seconds until the next Adhan. Hence, we can use it
    as a sort of countdown in which our program sleeps for that amount of seconds. Only once the program
    has slept that amount of time (at this point its Adhan time) does the notification for Adhan go off.
    """

    time_until_prayer = find_time_until_prayer(time_difference)

    time.sleep(time_until_prayer)

    prayer_notification(prayer)


def main():

    loop = True

    while loop:
        request = make_api_request(base_url, params)
        prayer_times_not_formatted = handle_api_request_response(request)
        current_time = get_current_time()
        prayer_times_formatted = format_prayer_times(prayer_times_not_formatted)
        check_for_next_prayer(prayer_times_formatted, current_time)



if __name__ == '__main__':
    main()
