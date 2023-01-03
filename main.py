import os, time, csv, json
from googleapiclient.discovery import build
from functools import reduce

API_KEY = os.getenv("YOUTUBE_DATA_API_V3_KEY")
youtube = build("youtube", "v3", developerKey=API_KEY)

# list of selected channels
channel_list = {"handel": [], "channel_id": []}
with open("channels-list.csv", "r") as f:
    channels = csv.DictReader(f)
    for row in channels:
        channel_list["handel"].append(row["handel"])
        channel_list["channel_id"].append(row["channel_id"])


# get channel info ----
## refer https://developers.google.com/youtube/v3/getting-started#fields

# comma separated channel ids
channel_ids = ", ".join(channel_list["channel_id"])
part = "snippet, statistics, topicDetails, contentDetails"
fields = (
        "snippet(title, description, publishedAt, country, thumbnails.high.url)",
        "statistics(viewCount, subscriberCount, videoCount)",
        "topicDetails.topicCategories",
        "contentDetails.relatedPlaylists.uploads"
        )

response_channel = youtube.channels().list(
    part=part, id=channel_ids, fields=f"items({', '.join(fields)})"
    ).execute()
response_channel = response_channel["items"]

# # write to disk
access_time = time.strftime("%F %T %Z")  # data access time
stem = f"channels-data_{access_time}"

# as json
with open(f"data/json/{stem}.json", "w") as json_file:
    json.dump(response_channel, json_file, indent=4)

# as csv
## flatten the first level (part) dict nesting -- removes (snipptet, statistics ...)
response_channel = list(map(lambda item: reduce(lambda x, y: {**x, **y}, item.values()), response_channel))
with open(f"data/{stem}.csv", "w") as csv_file:
    # fieldnames (correspond to `fields` above)
    fieldnames = list(response_channel[0].keys())
    
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    writer.writeheader()
    for item in response_channel:
        # flatten len 1 nested dict, alternative is pandas.json_normalize()
        try:
            item = item.copy()
            item["thumbnails"] = item["thumbnails"]["high"]["url"]
            item["relatedPlaylists"] = item["relatedPlaylists"]["uploads"]
        except KeyError:
            pass
        writer.writerow(item)


youtube.close()
