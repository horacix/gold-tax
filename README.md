# Gold Tax Calculator

This project calculates the updated cost basis and expense proceeds for precious metals ETFs.

## Requirements

- Python 3.6+
- pandas
- decimal

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/gold-tax.git
    cd gold-tax
    ```

2. Install the required packages:
    ```sh
    pip install pandas
    ```

## Usage

To run the script, use the following command:

```sh
python main.py -t TICKER -d DATE_ACQUIRED -n SHARES -p PRICE -y YEAR [-s DATE_SOLD]
```

## Arguments

- `-t`, `--ticker`: ETF Ticker (required)
- `-d`, `--date_acquired`: Date of purchase (m/d/y) (required)
- `-n`, `--shares`: Number of shares (required)
- `-p`, `--price`: Purchase price (required)
- `-y`, `--year`: Tax year (required)
- `-s`, `--date_sold`: Date of sale (m/d/y) (optional)

## Example

```sh
python main.py -t GLD -d 01/01/2020 -n 10 -p 150 -y 2021
```

## Description

The script performs the following steps:

1. Reads the ETF data from a CSV file.
2. Calculates the total ounces of gold owned based on the number of shares.
3. Calculates the cumulative ounces sold from a given date to cover expenses.
4. Calculates the cost basis of gold sold to cover expenses.
5. Calculates the gain or loss from the sale of shares.
6. Calculates the adjusted cost basis and remaining ounces of gold after selling shares to cover expenses in a given year.

## License

This project is licensed under the MIT License. See the LICENSE file for details.