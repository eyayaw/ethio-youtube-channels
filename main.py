import csv
import os
from datetime import datetime, timezone
from youtube_data import YouTubeData, Channel

OUTPUT_DIRECTORY = "data"  # dir for writing the data to

# Mostly, channel details are already set, or may not not change frequently. 
# So getting channel info for a channel once may be sufficient.

def _get_new_channel_ids(client: YouTubeData, channel_info_path: str) -> list[str]:
    if not os.path.exists(channel_info_path):
        return list(client.channels.keys())  # the first time, file DNE
    with open(channel_info_path, "r") as f:
        reader = csv.DictReader(f)
        existing_channel_ids = [row["id"] for row in reader]
        return list(set(client.channels.keys()) - set(existing_channel_ids))

def update_channel_info_on_new_ids(client: YouTubeData, channel_info_path: str) -> None:
    new_channel_ids = _get_new_channel_ids(client, channel_info_path)
    if new_channel_ids:
        client.channels = {id: Channel(id) for id in new_channel_ids}
        data_info = client.get_info()
        client.write_info(channel_info_path, data_info)
        print(f"{channel_info_path} has been updated with new channels data.")


def main() -> None:
    api_key = os.environ.get("YOUTUBE_DATA_API_V3_KEY")
    if not api_key:
        raise ValueError("YouTube Data API key not found in environment variables.")

    client = YouTubeData(api_key=api_key)
    client.add_channels_from_csv()

    os.makedirs(OUTPUT_DIRECTORY, exist_ok=True)

    # Get channel stats
    today = datetime.now(timezone.utc)
    channels_stats_path = f"{OUTPUT_DIRECTORY}/channels-data_{today:%Y-%m}.csv"
    data_stats = client.get_stats()
    client.write_stats(channels_stats_path, data_stats)
    print(f"{channels_stats_path} has been updated for {today:%Y-%m-%d}")

    # Get channel details
    channel_info_path = f"{OUTPUT_DIRECTORY}/channels-info.csv"
    update_channel_info_on_new_ids(client, channel_info_path)


if __name__ == "__main__":
    main()
