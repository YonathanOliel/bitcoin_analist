
def save_rates_data_to_file(point_and_wallet):
    f = open("DATA.txt", "a")
    f.write(point_and_wallet)
    

def compute_moving_average_for_rates_data(rates, nb_days_interval):
    s = 0
    averages = []

    for i in range(len(rates)):
        rate = rates[i]
        s += rate["value"]
        a = 0
        if i >= nb_days_interval:
            s -= rates[i-nb_days_interval]["value"]
            a = s / nb_days_interval
        else:
            a = s / (i+1)
        averages.append({"date": rate["date"], "value": a})
    return averages


def compute_buy_and_sell_points_from_ma(short_ma, long_ma, threshold_percent=0):
    buy_mode = True
    points = []

    for i in range(len(short_ma)):
        date_str = short_ma[i]["date"]
        sma_value = short_ma[i]["value"]
        lma_value = long_ma[i]["value"]
        mult = 1+threshold_percent/100
        if buy_mode:
            if sma_value > lma_value*mult:
                points.append((date_str, buy_mode))
                buy_mode = False
        else:
            if sma_value < lma_value/mult:
                points.append((date_str, buy_mode))
                buy_mode = True

    return points


def get_rate_value_for_date(rates, date):
    for r in rates:
        if r["date"] == date:
            return r["value"]
    return None


def compute_buy_and_sell_gains(initial_wallet, rates, buy_and_sell_points):
    current_wallet = initial_wallet
    last_wallet = 0
    shares = 0

    if buy_and_sell_points[-1][1]:
        buy_and_sell_points = buy_and_sell_points[:-1]
    for point in buy_and_sell_points:
        rate_value = get_rate_value_for_date(rates, point[0])
        if point[1]:
            print(f"on {point[0]} you buy {round(current_wallet, 3)} dollar of Bitcoin")
            save_rates_data_to_file("\nON: " + str(point[0]) + "\nYOU BUY " + str(current_wallet) + " DOLLAR OF BITCOIN\n") 
            shares = current_wallet / rate_value
            last_wallet = current_wallet
            current_wallet = 0
        else:
            current_wallet = shares * rate_value
            shares = 0
            print(f"on {point[0]} you sold {round(current_wallet, 3)} dollar of Bitcoin")
            save_rates_data_to_file("\nON: " + str(point[0]) + "\nYOU SOLD " + str(current_wallet) + " DOLLAR OF BITCOIN\n")
            if current_wallet > last_wallet:
                percent = (current_wallet-last_wallet) * 100/last_wallet
                print("you earned:", str(round(percent, 1))+"%")
                save_rates_data_to_file("YOU EARNED: " + str(round(percent, 1))+"%\n")
            else:
                percent = (last_wallet-current_wallet) * 100/last_wallet
                print("you lost:", str(round(percent, 1))+"%")
                save_rates_data_to_file("YOU LOST: " + str(round(percent, 1))+"%\n")
            print()
    return current_wallet





