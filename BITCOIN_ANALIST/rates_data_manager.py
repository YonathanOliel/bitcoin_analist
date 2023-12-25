from datetime import date, datetime, timedelta
from coinapi_service import coin_api_get_exchange_filtered_rates_extended
import json
from os import path


def load_json_data_from_file(filename):
    f = open(filename, "r")
    json_data = f.read()
    f.close()
    return json_data


def save_rates_data_to_file(filename, rates_data):
    json_data = json.dumps(rates_data)
    f = open(filename, "w")
    f.write(json_data)
    f.close()


def convert_rates_to_date_value_format(rates_data):
    rates_date_value_format = []

    for r in rates_data:
        rates_date_value_format.append({"date": r["time_period_start"][:10], "value": r["rate_close"] })
    return rates_date_value_format


def get_and_manage_rates_data(assets, date_start, date_end):
    FILE_NAME = assets.replace("/", "_") + ".json"
    rates = []
    exclude_nd_days_start = 0
    exclude_nd_days_end = 0
    
    if path.exists(FILE_NAME):
        json_rates = load_json_data_from_file(FILE_NAME)
        rates = json.loads(json_rates)

    if len(rates) > 0:
        saved_data_date_start_str = rates[0]["date"]
        saved_data_date_end_str = rates[-1]["date"]
       
        saved_data_date_start = datetime.strptime(saved_data_date_start_str, "%Y-%m-%d").date()
        saved_data_date_end = datetime.strptime(saved_data_date_end_str, "%Y-%m-%d").date()

        nb_days_start = (saved_data_date_start - date_start).days
        if nb_days_start > 0:
            rates_start = coin_api_get_exchange_filtered_rates_extended(assets, date_start, saved_data_date_start - timedelta(1))
            rates_start_date_value = convert_rates_to_date_value_format(rates_start)
            rates = rates_start_date_value + rates
        
        elif nb_days_start < 0:
            exclude_nd_days_start = -nb_days_start

        nb_days_end = (date_end - saved_data_date_end).days
        if nb_days_end > 0:
            rates_end = coin_api_get_exchange_filtered_rates_extended(assets, saved_data_date_end + timedelta(1), date_end)
            rates_end_date_value = convert_rates_to_date_value_format(rates_end)
            rates += rates_end_date_value

        elif nb_days_end < 0:
            exclude_nd_days_end = -nb_days_end

        save_rates_data_to_file(FILE_NAME, rates)
    else:
        rates_api = coin_api_get_exchange_filtered_rates_extended(assets, date_start, date_end)
        rates = convert_rates_to_date_value_format(rates_api)
        save_rates_data_to_file(FILE_NAME, rates)
    
    if exclude_nd_days_start > 0:
        rates = rates[exclude_nd_days_start:]

    if exclude_nd_days_end > 0:
        rates = rates[:-exclude_nd_days_end]

    return rates

