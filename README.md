# chase-transactions

Transforms transaction CSVs downloaded from Chase into the format for https://github.com/kac460/finance-predictions.

# Usage
1. Clone this repo.
2. Create a top-level directory in this project called `original/`
3. Place any number of Chase transactions CSVs into `original/`
4. Run `python3 transform.py`
5. Copy the outputted CSV into the Google Sheet referenced in [finance-predictions](https://github.com/kac460/finance-predictions) in the `Transactions` tab (e.g. paste into the 1st Expenses column and then Go to `Data` -> `Split into columns`)