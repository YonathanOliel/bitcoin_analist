from datetime import date, datetime, timedelta
from rates_data_manager import get_and_manage_rates_data
import matplotlib.pyplot as plt 
from rates_data_processing import*
from emails import sending_the_emails




TIME_START = date(2022, 1, 1)
TIME_END = date.today()-timedelta(1)
ASSETS = "BTC/USD"



rates = get_and_manage_rates_data(ASSETS, TIME_START, TIME_END)
print("number of rates:", len(rates))

ma_intervals = [8, 20]
ma_list = []

for interval in ma_intervals:
    ma = compute_moving_average_for_rates_data(rates, interval)
    ma_list.append((ma, interval))



buy_and_sell_points = compute_buy_and_sell_points_from_ma(ma_list[0][0], ma_list[1][0], 1)

initial_wallet = 1000
final_wallets_for_intervals = []
for i in range(len(ma_intervals)):
    for j in range(i+1, len(ma_intervals)):
        p = compute_buy_and_sell_points_from_ma(ma_list[i][0], ma_list[j][0], 1)
        final_wallet = compute_buy_and_sell_gains(initial_wallet, rates, p)
        final_wallets_for_intervals.append((ma_intervals[i], ma_intervals[j], final_wallet))


final_wallets_for_intervals.sort(key=lambda x: x[2], reverse=True)

print("Start date:", TIME_START)
print("Final date:", TIME_END)
print("entry value:", initial_wallet)
print("exit value:", round(final_wallet, 3))

rates_dates = [datetime.strptime(r["date"], "%Y-%m-%d") for r in rates]
rates_values = [r["value"] for r in rates]

plt.ylabel(ASSETS)
plt.plot(rates_dates, rates_values) 


for ma_item in ma_list:
    ma_values = [r["value"] for r in ma_item[0]]
    plt.plot(rates_dates, ma_values, label = "MA" + str(ma_item[1]))


for point in buy_and_sell_points:
    date_obj = datetime.strptime(point[0], "%Y-%m-%d")
    if point[1] == True:
        plt.axvline(x = date_obj, color = 'r')
    else:
        plt.axvline(x = date_obj, color = 'y')


plt.legend()
plt.show()


f = open("DATA.txt", "r")
d = f.read()
sending_the_emails("jhonnyoliel@gmail.com", d)
f.close()
