import argparse
import pandas as pd
from decimal import Decimal, getcontext, ROUND_HALF_UP

# Set the precision and rounding mode
getcontext().prec = 28
getcontext().rounding = ROUND_HALF_UP

def read_csv(f):
    df = pd.read_csv(f, parse_dates=["Date"], index_col="Date")
    # print(df.head())
    return df



def step1(df, date, shares):
    ounces_per_share = Decimal(df.loc[date, "OuncesPerShare"])
    shares = Decimal(shares)
    result = ounces_per_share * shares
    return result.quantize(Decimal('1.000000000'))



def step2(df, date, shares):
    cummulative_sale = Decimal(df[date:]["OuncesSold"].sum()) * Decimal(shares)
    return cummulative_sale.quantize(Decimal('1.000000000'))


def step3(ounces, sold, basis):
    cost = (sold/ounces) * Decimal(basis)
    return cost.quantize(Decimal('1.00'))


def step4(df, date, shares, cost_sold):
    proceeds = Decimal(df[date:]["ProceedsPerShare"].sum()) * Decimal(shares)
    gain_loss = proceeds - cost_sold
    return gain_loss.quantize(Decimal('1.00'))


def previous_years_basis(df, year, initial_basis, date, shares):
    ounces = initial_basis[1]
    sold = step2(df, date, shares)
    remaining = ounces - sold

    basis = Decimal(initial_basis[0])
    cost_sold = step3(ounces, sold, basis)
    adjusted_basis = basis - cost_sold

    return (adjusted_basis, remaining)


def main(args):
    ticker = args.ticker.lower()
    date = pd.to_datetime(args.date_acquired)
    basis = args.shares * args.price
    try:
        with open(ticker + ".csv", "r") as f:
            print(f"Using {ticker}.csv")
            # read into dataframe
            df = read_csv(f)

        print(f"Cost basis: ${basis}")

        year_acquired = date.year
        initial_basis = (basis, step1(df, date, args.shares))
        
        if year_acquired < args.year:
            y = year_acquired
            while y < args.year:
                dfy = df.loc[str(y)]
                initial_basis = previous_years_basis(dfy, y, initial_basis, date, args.shares)
                # set the date to the first day of the next year
                date = pd.to_datetime(str(y+1) + "-01-01")
                y += 1

        basis = initial_basis[0]
        print(f"Year start basis: ${basis.quantize(Decimal('1.00'))}")
        
        # Step 1: Identify the shareholder’s pro rata ownership of gold (in ounces).
        ounces = initial_basis[1]
        print(f"Year start ounces: {ounces}")

        print(f"Initial date: {date}")

        # Step 2: Calculate the gold (in ounces) sold from the shareholder’s account during the year
        ounces_sold = step2(df, date, args.shares)
        print(f"Ounces sold: {ounces_sold}")

        # Step 3: Calculate cost of gold sold from shareholder’s account
        cost_sold = step3(ounces, ounces_sold, basis)
        print(f"Cost sold: ${cost_sold}")

        # Step 4: Calculate shareholder’s gain or loss on sales of gold for each lot purchased
        gain_loss = step4(df, date, args.shares, cost_sold)
        print(f"Gain/Loss: ${gain_loss}")

        print(f"Year end basis: ${(basis - cost_sold).quantize(Decimal('1.00'))}")

    except FileNotFoundError:
        print(f"Could not find {args.ticker}.csv")
        exit(1)
    except KeyError:
        print(f"Date {args.date} not found.")
        exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate updated cost basis and expense proceeds for precious metals ETFs.")
    parser.add_argument("-t", "--ticker", type=str, help="ETF Ticker", required=True)
    parser.add_argument("-d", "--date_acquired", type=str, help="Date of purchase (m/d/y)", required=True)
    parser.add_argument("-n", "--shares", type=float, help="Number of shares", required=True)
    parser.add_argument("-p", "--price", type=float, help="Purchase price", required=True)
    parser.add_argument("-y", "--year", type=int, help="Tax year", required=True)
    parser.add_argument("-s", "--date_sold", type=str, help="Date of sale (m/d/y)", required=False)

    args = parser.parse_args()
    main(args)
