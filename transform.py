import csv
import os
from string import capwords
from datetime import datetime
from dataclasses import dataclass
import shutil


@dataclass
class TransformedTransaction:
    date: datetime
    amount: float
    description: str

    def dict_for_csv(self) -> dict[str, str | float]:
        return {
            "Date": datetime.strftime(self.date, "%Y-%m-%d"),
            "Amount": self.amount,
            "Description": self.description,
        }


# given Transaction Date,Post Date,Description,Category,Type,Amount,Memo
# transform into Date,Amount,Description
def transform(original: dict[str, str | float]) -> TransformedTransaction:
    return TransformedTransaction(
        date=datetime.strptime(original["Transaction Date"], "%m/%d/%Y"),
        amount=-1 * float(original["Amount"]),
        description=capwords(original["Description"]),
    )

def extract_plurality_month(transactions: list[TransformedTransaction]):
    month_counts: dict[str, int] = {}
    for txn in transactions:
        month = txn.date.month
        month_counts[month] = month_counts.get(month, 0) + 1
    return max(month_counts, key=month_counts.get)

def plurality_month_transactions(
    transactions: list[TransformedTransaction],
) -> list[TransformedTransaction]:
    plurality_month = extract_plurality_month(transactions)
    return [txn for txn in transactions if txn.date.month == plurality_month]


def no_auto_pay(
    transactions: list[TransformedTransaction],
) -> list[TransformedTransaction]:
    return [
        txn
        for txn in transactions
        if txn.description.strip() != "Automatic Payment - Thank"
    ]


def filtered_transactions(
    transactions: list[TransformedTransaction],
) -> list[TransformedTransaction]:
    plurality_only = plurality_month_transactions(transactions)
    return no_auto_pay(plurality_only)


def is_empty_dir(path_name: str) -> bool:
    return not os.path.isdir(path_name) or not os.listdir(path_name)


TO_PROCESS_PATH = "original/to-process"


def main() -> None:
    if is_empty_dir(TO_PROCESS_PATH):
        print(
            f"Put your Chase transactions CSVs into {TO_PROCESS_PATH} before running this script."
        )
        return
    run_datetime_str = datetime.strftime(datetime.now(), "%Y%m%d%H%M%S")
    files_to_process = os.listdir(TO_PROCESS_PATH)

    transformed_transactions: list[TransformedTransaction] = []

    for path_to_file_to_process in files_to_process:
        with open(f"{TO_PROCESS_PATH}/{path_to_file_to_process}") as f:
            csv_reader = csv.DictReader(f)
            transformed_transactions += [
                transform(transaction) for transaction in csv_reader
            ]
    transformed_transactions.sort(key=lambda txn: txn.date)
    transformed_file_name = f"{run_datetime_str}.csv"
    dicts_for_csv = [
        txn.dict_for_csv() for txn in filtered_transactions(transformed_transactions)
    ]
    if len(dicts_for_csv) == 0:
        print(f'No valid transactions in plurality month {extract_plurality_month(transformed_transactions)} to process! Check your data and then manually move to the archive folder if this seems correct.')
        return
    os.makedirs('transformed', exist_ok=True)
    transformed_file_path = f"transformed/{transformed_file_name}"
    with open(transformed_file_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=dicts_for_csv[0].keys())
        writer.writeheader()
        writer.writerows(dicts_for_csv)
        print(f"Transformed transactions written to {transformed_file_path}")

    dest_dir = f"original/archive/{run_datetime_str}"
    os.makedirs(dest_dir)
    for file_to_process in files_to_process:
        src = f"{TO_PROCESS_PATH}/{file_to_process}"
        dest = f"{dest_dir}/{file_to_process}"
        shutil.move(src, dest)


if __name__ == "__main__":
    main()
