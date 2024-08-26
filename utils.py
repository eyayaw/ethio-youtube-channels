import csv
from itertools import islice


# See pandas.json_normalize
def flatten_dict(d: dict, parent_key: str = "", sep: str = ".") -> dict:
    """
    Flattens a nested dictionary by concatenating keys with a separator.

    Args:
        d (dict): The dictionary to flatten.
        parent_key (str): The parent key to use for concatenation. Defaults to an empty string.
        sep (str): The separator to use for concatenation. Defaults to '.'.

    Returns:
        dict: The flattened dictionary.
    """
    items = []
    for k, v in d.items():
        # concatenate the parent key and current key with the separator
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            # recursively flatten nested dictionaries and extend the result to the items list
            nested_items = flatten_dict(v, new_key, sep=sep).items()
            items.extend(nested_items)
        else:
            # add the flattened key-value pair to the items list
            items.append((new_key, v))
    # return the flattened dictionary as a dictionary
    return dict(items)


def write_to_csv(file_path: str, data: list[dict], append=False):
    """
    Write data to a CSV file. Can append to file if it already exists.
    Parameters:
    - file_path (str): Path to the CSV file.
    - data (list of dicts): Data to be written to the CSV file. Each dict represents a row.
    - append (bool): If True, append data to the file. If False, overwrite the file.
    """

    if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
        raise TypeError("data should be a list of dictionaries")

    if not file_path.endswith(".csv"):
        raise Exception("The file path must have a `.csv` ext: `{path}`")

    fieldnames = list(data[0].keys())  # Take the col names from the first dict
    mode = "a" if append else "w"  # Append if True, else write

    with open(file_path, mode, newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not append:
            writer.writeheader()  # Header will be written only on write
        writer.writerows(data)


# https://docs.python.org/3/library/itertools.html#itertools.batched
## itertools.batched in 3.12
## Roughly equivalent to
def batched(iterable, n):
    # batched('ABCDEFG', 3) → ABC DEF G
    if n < 1:
        raise ValueError("n must be at least one")
    iterator = iter(iterable)
    while batch := tuple(islice(iterator, n)):
        yield batch
