import os, sys, csv
from typing import Sequence
from googleapiclient.discovery import build
from functools import reduce
from datetime import datetime, timezone

def get_channel_stats(api_key: str, channel_id: Sequence[str], **kwargs) -> list[dict]:
    """Retreive channel statistics from the YouTube Data API

    Args:
        api_key (str): YouTube Data API Key
        channel_id (Sequence[str]): A list of channel ids
        **kwargs: args passed to the `list()` method of the `channels()` resource.

    Returns:
        list: A list of dict of channel data
    """

    if isinstance(channel_id, (list, tuple)) and len(channel_id) > 1:
        channel_id = ", ".join(channel_id)

    part = ["snippet", "statistics"]
    fields = "items(%s)" % (", ".join(["snippet(title)","statistics(viewCount, subscriberCount, videoCount)"]))

    # send the request to the youtube data api
    youtube = build("youtube", "v3", developerKey=api_key)
    try:
        response = youtube.channels().list(part=part, id=channel_id, fields=fields, **kwargs).execute()
        retrieved_at = datetime.now(timezone.utc).strftime("%F %T %Z") #datetime.utcnow().strftime("%F %T UTC")
        response = response["items"]
        # append the date at which the data was retrieved to each channel result
        for item in response:
            item.update({"retrievedAt": {"retrievedAt": retrieved_at}})
        response = sorted(response, key=lambda x: x["snippet"]["title"])
    except Exception as e:
        sys.exit(f"err={e}")

    youtube.close()

    return response


def get_channel_info_static(api_key: str, channel_id: Sequence[str], **kwargs) -> list[dict]:
    """
    Retreive information about the channel from the YouTube Data API.
    Such information can be description, and topic details of the channel, country where it is located etc.
    And, mostly these info do not change constantly, are already set. 

    Args:
        api_key (str): YouTube Data API Key
        channel_id (Sequence[str]): A list of channel ids
        **kwargs: args passed to the `list()` method of the `channels()` resource.

    Returns:
        list: A list of dict of channel data
    """

    if isinstance(channel_id, (list, tuple)) and len(channel_id) > 1:
        channel_id = ", ".join(channel_id)

    part = ", ".join(["snippet"," topicDetails", "contentDetails"])
    fields = (
        "snippet(title, description, publishedAt, country, thumbnails.high.url)",
        "topicDetails.topicCategories",
        "contentDetails.relatedPlaylists.uploads"
        )
    fields = "items(%s)" %(", ".join(fields))

    # send the request to the youtube data api
    youtube = build("youtube", "v3", developerKey=api_key)
    try:
        response = youtube.channels().list(part=part, id=channel_id, fields=fields, **kwargs).execute()
        retrieved_at = datetime.now(timezone.utc).strftime("%F %T %Z")
        response = response["items"]
        response = sorted(response, key=lambda x: x["snippet"]["title"])
        print("Data accessed at: " + retrieved_at)
    except Exception as e:
        sys.exit(f"err={e}")

    youtube.close()

    return response


def write_channel_info(path: str, response_channel: list[dict]):
    if not path.endswith(".csv"):
        raise Exception("Path `{path}` should have a `.csv` ext.")

    ## flatten the first level (part) dict nesting -- removes (snipptet, ...)
    data = list(
        map(lambda item: reduce(lambda x, y: {**x, **y}, item.values()), response_channel)
    )

    with open(path, "w") as csv_file:
        
        # fieldnames (correspond to `fields` above)
        fieldnames = list(data[0].keys())
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()

        for item in data:
            # flatten len 1 nested dict, alternative is pandas.json_normalize()
            try:
                item = item.copy()
                item["thumbnails"] = item["thumbnails"]["high"]["url"]
                item["relatedPlaylists"] = item["relatedPlaylists"]["uploads"]
            except KeyError:
                pass
            writer.writerow(item)
    
    print(f"The data has been written to `{path}`.")


def append_stats(path: str, response_channel: list[dict]):
    # only statistics, snippet should be present
    if not all([p in response_channel[0].keys() for p in ["snippet", "statistics"]]):
        raise Exception("Only [snippet, statistics] as `part` parameter are allowed.")
    
    if not path.endswith(".csv"):
        raise Exception("Path `{path}` should have a `.csv` ext.")
    
    ## flatten the first level (part) dict nesting -- removes (snipptet, statistics)
    data = list(
        map(lambda item: reduce(lambda x, y: {**x, **y}, item.values()), response_channel)
    )

    file_exists = os.path.exists(path)
    with open(path, "a") as csv_file:
        
        # fieldnames (correspond to `fields` above)
        fieldnames = list(data[0].keys())
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        
        # when a new file is created (i.e., every month), write the header
        if not file_exists:
            writer.writeheader()
    
        for item in data:
            writer.writerow(item)
    
    print(f"The data (containing only stats) has been appended to `{path}`.")


def main():
    API_KEY = os.getenv("YOUTUBE_DATA_API_V3_KEY")
    # list of selected channels
    with open("channels-list.csv", "r") as f:
        reader = csv.DictReader(f)
        channel_list = [row["channel_id"] for row in reader]

    out_dir = "data/"  # dir for writing the data to
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    # put each month data seprately, otherwise we'll have a huge csv file
    mon_year = datetime.now(timezone.utc).strftime("%m-%Y")
    out_file = f"{out_dir}/channels-data_{mon_year}.csv"

    # get channels stats and append them
    channel_stats = get_channel_stats(API_KEY, channel_list)
    append_stats(out_file, channel_stats)

    # static data, and write it (running once is enough)
    channel_info_path = f"{out_dir}/channels-info.csv"
    if not os.path.exists(channel_info_path):
        channel_info = get_channel_info_static(API_KEY, channel_list)
        write_channel_info(channel_info_path, channel_info)


if __name__ == "__main__":
    main()