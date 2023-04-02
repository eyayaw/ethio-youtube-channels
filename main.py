# imports ----
# %%
import os
import csv
from googleapiclient.discovery import build
from datetime import datetime, timezone

# helper ----
# %%
def flatten_dict(d: dict, parent_key: str = '', sep: str = '.') -> dict:
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

# custom exception to catch empty response for disabled/inactive/terminated channel
class ChannelError(ValueError):
    pass

# retrievers ----
# %%
def get_channel_info_static(api_key: str, channel_ids: list[str], **kwargs) -> list[dict]:
    """
    Retreive information about the channel from the YouTube Data API.
    Such information can be the description, and topic details of the channel,
    the country where it is located at, etc.
    And, mostly these details are already set, or may not not change frequently. So calling this function for a channel once may be sufficient.

    Args:
        api_key (str): YouTube Data API Key
        channel_ids (list[str]): A list of channel ids
        **kwargs: args passed to the `list()` method of the `channels()` resource.

    Returns:
        list: A list of dict of channel data.
    """

    if isinstance(channel_ids, list) and len(channel_ids) > 1:
        channel_ids = ", ".join(channel_ids)

    part = ", ".join(["id", "snippet", "topicDetails", "contentDetails"])
    fields = (
        "id",
        "snippet(title, description, publishedAt, country, thumbnails.high.url)",
        "topicDetails.topicCategories",
        "contentDetails.relatedPlaylists.uploads"
        )
    fields = "items(%s)" %(", ".join(fields))

    # send the request to the youtube data api
    youtube = build("youtube", "v3", developerKey=api_key)
    try:
        response = youtube.channels().list(part=part, id=channel_ids, fields=fields, **kwargs).execute()
        retrieved_at = datetime.now(timezone.utc).strftime("%F %T %Z")
        if "items" not in response:
            raise ChannelError
        # print("The response is empty.\nThe channels do not exist, or are disabled or terminated by YouTube.")
        else:
            response_items = sorted(response["items"], key=lambda x: x["snippet"]["title"])
        print("Data accessed at: " + retrieved_at)
    except ChannelError:
        # response_items = []
        raise SystemExit(f"ChannelError: The channel(s) {channel_ids} is inactive/disabled/terminated.")
    except Exception as e:
        raise SystemExit(f"err={e}")
    finally:
        youtube.close()

    return response_items


def get_channel_stats(api_key: str, channel_ids: list[str], **kwargs) -> list[dict]:
    """Retreive channel statistics (number of views, subscribers, videos, etc.) from the YouTube Data API.

    Args:
        api_key (str): YouTube Data API Key
        channel_ids (list[str]): A list of channel ids
        **kwargs: args passed to the `list()` method of the `channels()` resource.

    Returns:
        list: A list of dict of channel data.
    """

    if isinstance(channel_ids, list) and len(channel_ids) > 1:
        channel_ids = ", ".join(channel_ids)

    part = ["id", "snippet", "statistics"]
    fields = "items(%s)" % (", ".join(["id", "snippet(title)","statistics(viewCount, subscriberCount, videoCount)"]))

    # send the request to the youtube data api
    youtube = build("youtube", "v3", developerKey=api_key)
    try:
        response = youtube.channels().list(part=part, id=channel_ids, fields=fields, **kwargs).execute()
        retrieved_at = datetime.now(timezone.utc).strftime("%F %T %Z")
        if "items" not in response:
            raise ChannelError
        else:
            response_items = response["items"]
            # append the date at which the data was retrieved to each item
            for item in response_items:
                item.update({"retrievedAt": retrieved_at})
            response_items = sorted(response_items, key=lambda x: x["snippet"]["title"])
    except ChannelError:
        # response_items = []
        raise SystemExit(f"ChannelError: The channel(s) {channel_ids} is inactive/disabled/terminated.")
    except Exception as e:
        raise SystemExit(f"err={e}")
    finally:
        youtube.close()

    return response_items


# writers ----
# %%
def write_channel_info(path: str, response_items: list[dict]):
    """
    Writes channel information to a CSV file.

    Args:
        path (str): The file path for the CSV file.
        reponse_items (list[Dict]): A list of dictionaries, each containing
            information about a channel.

    Raises:
        ValueError: If the file path does not have a '.csv' extension.
    """
    if not path.endswith(".csv"):
        raise Exception("The file path must have a `.csv` extension:`{path}`")

    ## flatten the nested dict/json, concatenates part + fields
    flattened_items = [flatten_dict(item) for item in response_items]

    file_exists = os.path.exists(path)
    with open(path, "a") as csv_file:
        # fieldnames (correspond to `fields` in `get_channel_info_static`) albeit flattened
        fieldnames = list(flattened_items[0].keys())
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerows(flattened_items)

    print(f"The data has been written to `{path}`.")


def write_channel_stats(path: str, response_items: list[dict]):
    # only statistics, snippet should be present
    if not all([p in response_items[0].keys() for p in ["snippet", "statistics"]]):
        raise Exception("Only [snippet, statistics] as `part` parameter are allowed.")

    if not path.endswith(".csv"):
        raise Exception("The file path must have a `.csv` ext: `{path}`")

    ## flatten the nested dict vals in each item
    flattened_items = [flatten_dict(item) for item in response_items]

    file_exists = os.path.exists(path)
    with open(path, "a") as csv_file:
        # fieldnames (correspond to `fields` above) albeit flattened
        fieldnames = list(flattened_items[0].keys())
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        # when a new file is created (i.e., every month), write the header
        if not file_exists:
            writer.writeheader()
        writer.writerows(flattened_items)

    print(f"The data (containing only stats) have been appended to `{path}`.")

# def main ----
# %%
def main():
    API_KEY = os.getenv("YOUTUBE_DATA_API_V3_KEY")
    # list of selected channels
    with open("channels-list.csv", "r") as f:
        reader = csv.DictReader(f)
        channel_ids = [row["channel_id"] for row in reader]

    out_dir = "data/"  # dir for writing the data to
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    # put each month data seprately, otherwise we'll have a huge csv file
    mon_year = datetime.now(timezone.utc).strftime("%m-%Y")
    out_file = f"{out_dir}/channels-data_{mon_year}.csv"

    # get channels stats and write/append them
    try:
        channel_stats = get_channel_stats(API_KEY, channel_ids)
    except SystemExit:
        pass
    else:
        write_channel_stats(out_file, channel_stats)

    # get static data, and write to csv file
    ## gets executed if new channel is added to `channels-list.csv`
    channel_info_path = f"{out_dir}/channels-info.csv"
    if os.path.exists(channel_info_path):
        # list of existing channel ids
        with open(channel_info_path, "r") as f:
            reader = csv.DictReader(f)
            existing_channel_ids = [row["id"] for row in reader]
        new_channel_ids = list(set(channel_ids) - set(existing_channel_ids))
    else:
        new_channel_ids = channel_ids # if for the first time (file DNE)
    if new_channel_ids:
        try:
            channel_info = get_channel_info_static(API_KEY, new_channel_ids)
        except SystemExit:
            pass
        else:
            write_channel_info(channel_info_path, channel_info)

# run main() ----
# %%
if __name__ == "__main__":
    main()
