import os, time, csv, json
from googleapiclient.discovery import build

API_KEY = os.getenv("YOUTUBE_DATA_API_V3_KEY")

# list of selected channels
channel_list = {"handel": [], "channel_id": []}
with open("channels-list.csv", "r") as f:
    channels = csv.DictReader(f)
    for row in channels:
        channel_list["handel"].append(row["handel"])
        channel_list["channel_id"].append(row["channel_id"])

youtube = build("youtube", "v3", developerKey=API_KEY)

# get channel info ----
## refer https://developers.google.com/youtube/v3/getting-started#fields

# comma separated channel ids
channel_ids = ", ".join(channel_list["channel_id"])

response_channel = (
    youtube.channels()
    .list(
        part="snippet,statistics",
        id=channel_ids,
        fields="items(snippet(title), statistics)",
    )
    .execute()
)

response_channel = response_channel["items"]

# # write to disk
acess_time = time.strftime("%F %T %Z")  # data access time
stem = f"channels-data_{acess_time}"

# as json
with open(f"data/{stem}.json", "w") as json_file:
    json.dump(response_channel, json_file)

# as csv
with open(f"data/{stem}.csv", "w") as csv_file:
    #fieldnames = ["title", "viewCount","subscriberCount","hiddenSubscriberCount","videoCount",]
    fieldnames = [
        *list(response_channel[0]["snippet"].keys()),
        *list(response_channel[0]["statistics"].keys()),
    ]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()
    for item in response_channel:
        writer.writerow({**item["snippet"], **item["statistics"]})


youtube.close()
