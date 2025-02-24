import argparse
import pandas as pd
from decimal import Decimal, getcontext, ROUND_HALF_UP

# Set the precision and rounding mode
getcontext().prec = 28
getcontext().rounding = ROUND_HALF_UP


def read_csv(f):
    df = pd.read_csv(f, parse_dates=["Date"], index_col="Date")
    return df


def step1(df, date, shares):
    """
    Calculate the total ounces of gold ownedbased on the number of shares.

    Args:
        df (pandas.DataFrame): DataFrame containing the data with a column "OuncesPerShare".
        date (str or datetime-like): The date to look up in the DataFrame.
        shares (float): The number of shares.

    Returns:
        Decimal: The total ounces of gold, rounded to 8 decimal places.
    """
    ounces_per_share = Decimal(df.loc[date, "OuncesPerShare"])
    shares = Decimal(shares)
    result = ounces_per_share * shares
    return result.quantize(Decimal("1.00000000"))


def step2(df, date, shares):
    """
    Calculate the cumulative ounces sold from a given date to cover expenses.

    Args:
        df (pandas.DataFrame): The dataframe containing sales data with a column 'OuncesSold'.
        date (str): The starting date from which to calculate the cumulative sale.
        shares (float): The number of shares to adjust the cumulative sale.

    Returns:
        Decimal: The cumulative sale adjusted by the number of shares, rounded to 8 decimal places.
    """
    cummulative_sale = Decimal(df[date:]["OuncesSold"].sum()) * Decimal(shares)
    return cummulative_sale.quantize(Decimal("1.00000000"))


def step3(ounces, sold, basis):
    """
    Calculate the cost basis of gold sold to cover expenses.

    Args:
        ounces (Decimal): The total number of ounces of gold (from step 1).
        sold (Decimal): The amount of gold sold (from step 2).
        basis (float): The initial cost basis of the gold.

    Returns:
        Decimal: The cost of gold sold, rounded to two decimal places.
    """
    cost = (sold / ounces) * Decimal(basis)
    return cost.quantize(Decimal("1.00"))


def step4(df, date, shares, cost_sold):
    """
    Calculate the gain or loss from the sale of shares.

    Args:
        df (pandas.DataFrame): DataFrame containing stock data with a 'ProceedsPerShare' column.
        date (str): The date from which to start calculating proceeds.
        shares (float): The total number of shares.
        cost_sold (Decimal): The cost of the shares sold (from step 3).

    Returns:
        Decimal: The gain or loss from the sale of shares, rounded to two decimal places.
    """
    proceeds = (
        Decimal(df[date:]["ProceedsPerShare"].sum()) * Decimal(shares)
    ).quantize(Decimal("1.00"))
    gain_loss = proceeds - cost_sold
    return gain_loss


def previous_years_basis(df, initial_basis, date, shares):
    """
    Calculate the adjusted cost basis and remaining ounces of gold after selling shares to cover expenses in a given year.

    Args:
        df (pd.DataFrame): DataFrame containing the expense data for a given year.
        initial_basis (tuple): A tuple containing the initial cost basis and ounces of gold.
        date (str): The initial date of ownership.
        shares (float): The number of shares owned.

    Returns:
        tuple: A tuple containing the adjusted basis (Decimal) and remaining ounces of gold (Decimal).
    """
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
    basis = Decimal(args.shares * args.price).quantize(Decimal('1.00'))
    try:
        with open(ticker + ".csv", "r") as f:
            print(f"Using {ticker}.csv")
            # read into dataframe
            df = read_csv(f)

        print(f"Purchase cost basis: ${basis}")

        year_acquired = date.year
        initial_basis = (basis, step1(df, date, args.shares))

        if year_acquired < args.year:
            y = year_acquired
            while y < args.year:
                dfy = df.loc[str(y)]
                initial_basis = previous_years_basis(
                    dfy, initial_basis, date, args.shares
                )
                # set the date to the first day of the next year
                date = pd.to_datetime(str(y + 1) + "-01-01")
                y += 1

        print(f"Starting date: {date}")

        basis = initial_basis[0]
        print(f"Starting cost basis: ${basis}")

        end_date = pd.to_datetime(str(args.year) + "-12-31")
        if args.date_sold:
            end_date = pd.to_datetime(args.date_sold)

        df = df.loc[date:end_date]

        # Step 1: Identify the shareholder’s pro rata ownership of gold (in ounces).
        ounces = initial_basis[1]
        print(f"Starting pro rata amount of gold: {ounces} oz")

        # Step 2: Calculate the gold (in ounces) sold from the shareholder’s account during the year
        ounces_sold = step2(df, date, args.shares)
        print(f"Amount of gold sold: {ounces_sold} oz")

        # Step 3: Calculate cost of gold sold from shareholder’s account
        cost_sold = step3(ounces, ounces_sold, basis)
        print(f"Cost of gold sold: ${cost_sold}")

        # Step 4: Calculate shareholder’s gain or loss on sales of gold for each lot purchased
        gain_loss = step4(df, date, args.shares, cost_sold)
        print(f"Gain/Loss: ${gain_loss}")

        # Step 5: Calculate shareholder’s adjusted cost basis
        print(f"Adjusted basis: ${basis - cost_sold}")

    except FileNotFoundError:
        print(f"Could not find {args.ticker}.csv")
        exit(1)
    except KeyError:
        print(f"Date {args.date} not found.")
        exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Calculate updated cost basis and expense proceeds for precious metals ETFs."
    )
    parser.add_argument("-t", "--ticker", type=str, help="ETF Ticker", required=True)
    parser.add_argument(
        "-d",
        "--date_acquired",
        type=str,
        help="Date of purchase (m/d/y)",
        required=True,
    )
    parser.add_argument(
        "-n", "--shares", type=float, help="Number of shares", required=True
    )
    parser.add_argument(
        "-p", "--price", type=float, help="Purchase price", required=True
    )
    parser.add_argument("-y", "--year", type=int, help="Tax year", required=True)
    parser.add_argument(
        "-s", "--date_sold", type=str, help="Date of sale (m/d/y)", required=False
    )

    args = parser.parse_args()
    main(args)
