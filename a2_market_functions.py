import os
import glob
import csv
import time


def item_analyser(action='buy', display=True):
    try:
        path = max(glob.iglob(r'C:\Users\Matt\Documents\EVE\logs\Marketlogs\*.txt'), key=os.path.getctime)
        base = os.path.basename(path)
        item = os.path.splitext(base)[0]
        name_start = item.find('-') + 1
        name = item[name_start:-18]
    except:
        print('\nNo market files exist yet')
        return

    with open('{}'.format(path)) as inF:
        orders = list(csv.reader(inF))

    buy_orders = []
    sell_orders = []
    for row in orders:
        try:
            if float(row[13]) < 2:
                if row[7] == 'True':
                    buy_orders.append(row)
                if row[7] == 'False':
                    sell_orders.append(row)
        except:
            pass

    broker_fee = 0.015
    transaction_tax = 0.036

    bestSale = float(sell_orders[0][0])
    best_sale_string = f'{float(bestSale):.2f}'.replace('.', '')
    sigfig = 6 - len(best_sale_string)
    adjustment = 10 ** (-sigfig)
    new_sale = bestSale - adjustment
    sell_order_after_tax = new_sale * (1 - broker_fee - transaction_tax)

    bestBuy = float(buy_orders[0][0])
    best_buy_string = f'{float(bestBuy):.2f}'.replace('.', '')
    sigfig = 6 - len(best_buy_string)
    adjustment = 10 ** (-sigfig)
    new_buy = bestBuy + adjustment
    buy_order_after_tax = new_buy * (1 + broker_fee + transaction_tax)


    sell_to_buy = bestBuy*(1-transaction_tax)
    # relist_profit = float(sell_orders[1][0]) * (1 - broker_fee - transaction_tax) - bestSale
    # relistROI = round(relist_profit / bestSale * 100, 2)
    # buy_price_after_fees = bestBuy * (1 + broker_fee)
    # sell_price_after_fees = bestSale * (1 - broker_fee - transaction_tax)
    #
    # if relistROI > 5:
    #     print('+++ Relist top sale for {}% ROI +++'.format(relistROI))
    # profit = round(sell_price_after_fees - buy_price_after_fees)
    # ROI = round(profit / buy_price_after_fees * 100, 2)

    if action == 'sell':
        new_price = new_sale
        pricejump = round(100 * ((float(sell_orders[1][0]) - bestSale) / bestSale), 2)

    if action == 'buy':
        new_price = new_buy
        pricejump = round(100*((bestBuy - float(buy_orders[1][0]))/float(buy_orders[1][0])), 2)

    if display is True:
        print('\n--------------------------------------------------')
        print(name)
        # print('ROI: {:,.2f}%   -+-   {:,.2f} ISK'.format(ROI, profit))

        if action == 'buy':
            print(f'buy order after fees {buy_order_after_tax:,.2f}')
            buy_diff = bestSale - buy_order_after_tax
            print(f'New {action} price: {new_price:,.2f} ISK')
            print(f'ISK saved:         {buy_diff:,.2f}')
        if action == 'sell':
            print(f'Sell:        {sell_order_after_tax:,.2f} \nSell-to-Buy: {sell_to_buy:,.2f}')
            sell_diff = sell_order_after_tax - sell_to_buy
            print(f'              {sell_diff:,.2f}')
            print(f'    {100*sell_diff/sell_order_after_tax:,.2f}%')
            print(f'New {action} price: {new_price:,.2f} ISK')

        # print(f"With broker's fee: {after_tax_price:,.2f} ISK ")

    return new_price

# item_analyser(action='sell', display=True)