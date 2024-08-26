import csv
import os
from googleapiclient.discovery import build
from datetime import datetime, timezone
from utils import flatten_dict, write_to_csv
from itertools import batched

# Constants
CSV_CHANNELS_LIST_PATH = "channels-list.csv"
CHANNEL_ID_COLUMN = "channel_id"
API_VERSION = "v3"  # for api service "youtube"


class ChannelError(ValueError):
    """Raised when there is an issue with a channel (inactive, disabled or terminated)."""

    pass


class APIError(Exception):
    """Raised when there is an API-related error (e.g. HTTPError)."""

    pass


class Channel:
    def __init__(self, channel_id) -> None:
        self.channel_id = channel_id
        self.channel_info = None
        self.channel_stats = None

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}("{self.channel_id}")'


class YouTubeData:
    def __init__(self, api_key: str):
        self.__api_key = api_key
        self.channels: dict[str, Channel] = {}

    def add_channel(self, channel_id: str) -> None:
        if not isinstance(channel_id, str):
            raise TypeError(f"channel_id should be of type str, got {type(channel_id)}")
        if channel_id not in self.channels:
            self.channels[channel_id] = Channel(channel_id)

    def add_channels(self, channel_ids: list[str]) -> None:
        if not isinstance(channel_ids, list):
            raise TypeError(
                f"channel_ids should be of type list, got {type(self.channel_ids)}"
            )
        for channel_id in channel_ids:
            self.add_channel(channel_id)

    def add_channels_from_csv(self, csv_path=CSV_CHANNELS_LIST_PATH):
        # The csv file should contain channel_id in the header
        with open(csv_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.add_channel(row[CHANNEL_ID_COLUMN])

    def get_info(self, **kwargs):
        """
        Retrieve information about the channel from the YouTube Data API.
        Such information can be the description, and topic details of the channel,
        the country where it is located at, etc. And, mostly these details are already set, or may not not change frequently.
        So calling this function for a channel once may be sufficient.

        Args:
            channel_ids (list[str]): A list of channel ids
            **kwargs: args passed to the `list()` method of the `channels()` resource.

        Returns:
            list: A list of dict of channel data.
        """
        params = self._channels_params("info")
        channel_ids = list(self.channels.keys())
        try:
            response_items = self._make_api_request(
                channel_id=channel_ids,
                part=params["part"],
                fields=params["fields"],
                **kwargs,
            )
            for item in response_items:
                self.channels[item["id"]].channel_info = item
            return sorted(response_items, key=lambda x: x["snippet"]["title"])
        except APIError as e:
            print(f"Some error has occurred: {e}")
            return []

    def get_stats(self, **kwargs):
        """Retrieve channel statistics (number of views, subscribers, videos, etc.) from the YouTube Data API.

        Args:
            channel_ids (list[str]): A list of channel ids
            **kwargs: args passed to the `list()` method of the `channels()` resource.

        Returns:
            list: A list of dict of channel data.
        """
        params = self._channels_params("stats")
        channel_ids = list(self.channels.keys())
        try:
            response_items = self._make_api_request(
                channel_id=channel_ids,
                part=params["part"],
                fields=params["fields"],
                **kwargs,
            )
            retrieved_at = datetime.now(timezone.utc).strftime("%F %T %Z")
            # append the date at which the data was retrieved to each item
            for i, item in enumerate(response_items):
                response_items[i].update({"retrievedAt": retrieved_at})
                self.channels[item["id"]].channel_stats = response_items[i]

            return sorted(response_items, key=lambda x: x["snippet"]["title"])
        except APIError as e:
            print(f"Some error has occurred: {e}")
            return []

    def _make_api_request(self, channel_id, part, fields, **kwargs):
        chunks = batched(channel_id, 50)
        response_items = []
        try:
            with DataAPIClient(self.__api_key) as client:
                for chunk in chunks:
                    res = (
                        client.youtube.channels()
                        .list(
                            id=",".join(chunk),
                            part=part,
                            fields=fields,
                            **kwargs,
                        )
                        .execute()
                    )
                    response_items.extend(res.get("items", []))
                    if "items" not in res:
                        print(
                            "ChannelError: The channel id(s) may have been disabled/terminated or is inactive."
                        )
        except Exception as e:
            raise APIError(f"Some error has occurred: {e}")

        return response_items

    @staticmethod
    def _channels_params(channel_data_type: str):
        choices = ["info", "stats"]
        if channel_data_type not in choices:
            raise ValueError(f"channel_data_type should be one of {choices}")
        if channel_data_type == "info":
            part = ",".join(["id", "snippet", "topicDetails", "contentDetails"])
            fields = (
                "id",
                "snippet(title, description, publishedAt, country, thumbnails.high.url)",
                "topicDetails.topicCategories",
                "contentDetails.relatedPlaylists.uploads",
            )
            fields = "items(%s)" % (",".join(fields))
        elif channel_data_type == "stats":
            part = ",".join(["id", "snippet", "statistics"])
            fields = [
                "id",
                "snippet(title)",
                "statistics(viewCount, subscriberCount, videoCount)",
            ]
            fields = "items(%s)" % (", ".join(fields))
        return {"part": part, "fields": fields}

    @staticmethod
    def write_info(file_path: str, response_items: list[dict]):
        """
        Writes channel info to a CSV file.
        Args:
            file_path (str): The file path for the CSV file.
            reponse_items (list[Dict]): A list of dicts, each containing info about a channel.
        """
        YouTubeData._write_data(file_path, response_items)

    @staticmethod
    def write_stats(file_path: str, response_items: list[dict]):
        # Only statistics, snippet should be present
        if not all([p in response_items[0].keys() for p in ["snippet", "statistics"]]):
            raise Exception(
                "Only [snippet,statistics] as `part` parameter are allowed."
            )
        YouTubeData._write_data(file_path, response_items)

    @staticmethod
    def _write_data(file_path, data):
        # flatten the nested dict vals in each item
        flattened = [flatten_dict(item) for item in data]
        # when a new file is created (e.g., every month for stats), write the header
        append = os.path.exists(file_path)
        write_to_csv(file_path, flattened, append=append)


class DataAPIClient:
    def __init__(self, api_key: str):
        self.youtube = build("youtube", API_VERSION, developerKey=api_key)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.youtube.close()
