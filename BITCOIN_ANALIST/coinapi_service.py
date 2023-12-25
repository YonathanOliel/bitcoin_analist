import requests
import json
from coinapi_config import API_KEY, BASE_URL
from datetime import timedelta



HEADERS = {'X-CoinAPI-Key': API_KEY}



def get_dates_intervals(date_start, date_end, max_days):
    diff = date_end-date_start
    diff_days = diff.days
    dates_intervals = []
    interval_begin_date = date_start

    while diff_days > 0:
        nb_days_to_add = max_days-1
        if diff_days < max_days-1:
            nb_days_to_add = diff_days
        interval_end_date = interval_begin_date + timedelta(nb_days_to_add)
        dates_intervals.append([interval_begin_date, interval_end_date])
        diff_days -= nb_days_to_add+1
        interval_begin_date = interval_end_date + timedelta(1)

    return dates_intervals


def coin_api_get_exchange_rates_extended(assets, start_date, end_date):
    rates = []

    dates_intervals = get_dates_intervals(start_date, end_date, 100)
    if len(dates_intervals) > 0:
        for i in dates_intervals:
            rates += coin_api_get_exchange_rates(assets, i[0], i[1])
    return rates


def coin_api_get_exchange_filtered_rates_extended(assets, start_date, end_date):
    rates = coin_api_get_exchange_rates_extended(assets, start_date, end_date)
    filtered_rates = filter_inconsistent_rate_values(rates)
    return filtered_rates


def rate_is_inconsistent(rate):
    v = rate["rate_open"]
    vmin = v / 10
    vmax = v * 10

    if not vmin <= rate["rate_close"] <= vmax:
        return True
    if not vmin <= rate["rate_high"] <= vmax:
        return True
    if not vmin <= rate["rate_low"] <= vmax:
        return True
    return False


def filter_inconsistent_rate_values(input_rates):
    if len(input_rates) < 2:
        return input_rates
    filtered_rates = []
    for i in range(len(input_rates)):
        r = input_rates[i]
        if rate_is_inconsistent(r):
            reference_rate = None
            if i > 0:
                reference_rate = input_rates[i-1]
            else:
                reference_rate = input_rates[i+1]
            patched_rate = r
            patched_rate["rate_open"] = reference_rate["rate_open"]
            patched_rate["rate_close"] = reference_rate["rate_close"]
            patched_rate["rate_high"] = reference_rate["rate_high"]
            patched_rate["rate_low"] = reference_rate["rate_low"]
            filtered_rates.append(patched_rate)
        else:
            filtered_rates.append(r)

    return filtered_rates


def coin_api_get_exchange_rates(assets, start_date, end_date):
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = (end_date + timedelta(1)).strftime("%Y-%m-%d")

    url = BASE_URL + "v1/exchangerate/" +\
          assets + "/history?period_id=1DAY&time_start=" +\
          start_date_str + "T00:00:00&time_end=" + end_date_str + "T00:00:00"

    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        print("The API call worked successfully")
        data = json.loads(response.text)
        print("The remaining readings:", response.headers["x-ratelimit-remaining"])
        return data
    else:
        print("The call to the API returned an error message:", response.status_code)
        return None
