

<!-- README.md is generated from README.qmd. Please edit that file -->

# Ethiopian Political YouTube Channels Daily Statistics

This repository contains a Python script that collects daily statistics,
such as view count, subscriber count, and video count, from a selected
list of Ethiopian YouTube channels that have political proclivities or
heavily discuss Ethiopian politics.

The script `main.py` has been running since `January 01, 2023`, see
[.`/data/channels-data_01-2023.csv`](./data/channels-data_01-2023.csv).
The repo also includes R scripts for generating charts based on the
collected data. You can use this repo to collect daily statistics of
other YouTube channels, see the [Usage](#usage) section below.

## Table of Contents

- [Overview](#overview)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Visualizing Data](#visualizing-data)
- [Contributing](#contributing)

## Overview

The purpose of this project is to gather daily insights and analyze the
impact of Ethiopian political YouTube channels on their audience. By
collecting and processing data such as view count, subscriber count, and
video count, we can better understand the reach and influence of these
channels in the Ethiopian political landscape, and identify which
channels are more popular.

<details>
<summary>
View a snapshot of stats
</summary>

| id | statistics.viewCount | statistics.subscriberCount | statistics.videoCount |
|:---|---:|---:|---:|
| [Abc tv](https://youtube.com/channel/UCTA1qWa_OFVl7OZ6DrEwRwg) | 200828 | 11600 | 131 |
| [Addis Compass Media / ACM / አዲስ ኮምፓስ ሚዲያ](https://youtube.com/channel/UCwUJ_Zli745ZoImP4IljpYg) | 14583797 | 72200 | 1058 |
| [AddisWalta - AW](https://youtube.com/channel/UC4yEV6VBe0Emu8sMpyij0uQ) | 60630014 | 459000 | 23112 |
| [Adebabay Media](https://youtube.com/channel/UC-kDmfnktrzc_SGpS9ulrXw) | 14682322 | 107000 | 1035 |
| [Alpha Media አልፋ ሚዲያ](https://youtube.com/channel/UCUyDe7EvbwwDRjyjUFU5Zhw) | 9614769 | 56000 | 1719 |
| [Andafta](https://youtube.com/channel/UCwMHDoJO6cHO6LN1BItFsPQ) | 317144179 | 988000 | 7769 |
| [Arat Kilo Media አራት ኪሎ ሚዲያ](https://youtube.com/channel/UCK71ZGx5VYTWw2XQ0F_O0nQ) | 712570 | 16500 | 90 |
| [DW Amharic](https://youtube.com/channel/UC3-RNH75BEZslJLEoIAxa2A) | 261164 | 9800 | 256 |
| [EBC](https://youtube.com/channel/UCOhrz3uRCOHmK6ueUstw7_Q) | 508033529 | 1490000 | 69427 |
| [EMS (Ethiopian Media Services)](https://youtube.com/channel/UCCJbY4YdJIUk7Lygrkg5IRA) | 94474168 | 370000 | 2592 |
| [ESAN TV](https://youtube.com/channel/UC5_7TzCp7YndNhVLo9top9A) | 3087032 | 42600 | 106 |
| [ESATtv Ethiopia](https://youtube.com/channel/UCSYM-vgRrMYsZbG-Z7Kz0Pw) | 213553058 | 699000 | 11359 |
| [EVN for Ethiopia](https://youtube.com/channel/UCuJQBlbbVB-3pZKLDxDI4HA) | 3051920 | 46500 | 242 |
| [Ethio Forum ኢትዮ ፎረም](https://youtube.com/channel/UCXUFyN9Ys5tiIHgJFQKRJvA) | 328906250 | 830000 | 2103 |
| [Ethio News - ኢትዮ ኒውስ](https://youtube.com/channel/UCelbYFUaQW3eb9sg3004ZGw) | 39301147 | 194000 | 1836 |
| [Ethio News_ኢትዮ ኒውስ ቻናል 2](https://youtube.com/channel/UC_m5g0TeOmYTPb535BLWd9Q) | 7504644 | 70800 | 251 |
| [Ethio Selam](https://youtube.com/channel/UCoVL5YOr2KdnYNspQf3s5uw) | 2134367 | 67000 | 88 |
| [EthioTube](https://youtube.com/channel/UCCk2vUhB0SyQhA6JXyjXHEg) | 44496132 | 266000 | 1925 |
| [Fana Television](https://youtube.com/channel/UCZtXd8pSeqURf5MT2fqE51g) | 435002971 | 1480000 | 45473 |
| [Feta Daily News](https://youtube.com/channel/UCgBnBckSLo6-uAiejtnEycQ) | 249292345 | 827000 | 1872 |
| [GEBEYANU](https://youtube.com/channel/UCb9fEB6StrknyRiSSzQ7H0A) | 14007827 | 139000 | 836 |
| [Horizon Free Media ሆራይዝን ነፃ ሚዲያ](https://youtube.com/channel/UCNgwbT7BCcppLG3zDm9f5UA) | 3583645 | 49800 | 195 |
| [Mager Media - ማገር](https://youtube.com/channel/UCilWrw2C8_VkFZ2tE5eKpdQ) | 2316530 | 34300 | 450 |
| [Mengizem Media ምንጊዜም ሚዲያ](https://youtube.com/channel/UCZvMKrP8XmP9GAHMloucOaA) | 8171838 | 69900 | 2501 |
| [OMN](https://youtube.com/channel/UCmAnzjcjIgtWuE6AnBCViTg) | 143027902 | 683000 | 12456 |
| [Reyot](https://youtube.com/channel/UCPVr1rrKl8pXVFi-rrqzS1g) | 68142059 | 263000 | 2610 |
| [Roha](https://youtube.com/channel/UCDXU7RuIQc0xRKJyP0ZTZaQ) | 47947539 | 235000 | 2078 |
| [Terara Network](https://youtube.com/channel/UC_f89AbX5NPU77YaoaSKRSg) | 3727641 | 52800 | 285 |
| [Tigrai Media House](https://youtube.com/channel/UCBvvcSYeDriczyImdI1qZWw) | 161231551 | 373000 | 6438 |
| [VOA Amharic](https://youtube.com/channel/UC5OePohJjdkd0Uwm3r1cThA) | 13280504 | 151000 | 7263 |
| [Wazema Radio](https://youtube.com/channel/UCQwdCM4dBMgxPh0UZa8PIow) | 2692496 | 50300 | 1545 |
| [Zara Media Network - ዛራ](https://youtube.com/channel/UCJ61rOk0c0b0COn0qOOo1aQ) | 1291408 | 143000 | 0 |
| [ebstv worldwide](https://youtube.com/channel/UCVcc_sbg3AcXLV9vVufJrGg) | 1360838470 | 2600000 | 26042 |
| [ዓባይ ዜና - Abbay News](https://youtube.com/channel/UC6bam4pQbuUgXnmyEFlSpNA) | 33039618 | 440000 | 1979 |

Snapshot of stats as of 2024-08-01 23:05:10

</details>

## Requirements

- Python 3.6 or higher
- [google-api-python-client](https://github.com/googleapis/google-api-python-client)
  package
- R dependencies: `data.table` and `ggplot2`
- [Quarto](https://quarto.org) (for rendering chart.qmd)

## Installation

1.  Clone this repository:

    ``` bash
    git clone https://github.com/eyayaw/ethio-youtube-channels.git
    ```

2.  Change the directory to the cloned repository:

    ``` bash
    cd ethio-youtube-channels
    ```

3.  Install the required Python package:

    ``` bash
    pip install -r requirements.txt
    ```

# Usage

1.  To use the script, you’ll need to obtain a Google API key. Follow
    the instructions in the [Google API Console
    documentation](https://developers.google.com/youtube/registering_an_application)
    to create a project and obtain an API key. Please read the [YouTube
    Data API getting
    started](https://developers.google.com/youtube/v3/getting-started).

2.  Set the API key as an environment variable named
    `YOUTUBE_DATA_API_V3_KEY` :
    `export YOUTUBE_DATA_API_V3_KEY=your_api_key`

3.  Update the  channels-list.csv  file with the list of YouTube channel
    IDs that you want to collect daily statistics about/from. Add one
    channel ID per row.

4.  Run the script: `python main.py`

5.  The script will generate a CSV file named
     `channels-data_MM-YYYY.csv`  (where MM is the month and YYYY is the
    year, generated automatically as the script runs) in the  `data` 
    folder containing the daily statistics for each channel in the
     `channels-list.csv`  file. Additionally, “static” information of
    the channels given in `channels-list.csv` will be written to
    `data/channels-info.csv`, and will be updated when new channels are
    added to the list.

# Visualizing Data

1.  Install the required R packages by running the following command in
    the R console: `install.packages(c("ggplot2", "data.table"))`

2.  Open the  `make-plots.R`  script and modify the input file name to
    match the latest CSV file in the  data  folder.

3.  Run the  `make-plots.R`  script to generate an interactive chart and
    save it as  chart.html.

4.  Install Quarto and use it to render the  `analysis.qmd`  file.

# Contributing

I highly welcome contributions to this project. If you want to add new
features, fix bugs, or improve documentation, please submit a pull
request or open an issue.

------------------------------------------------------------------------

> # Inspired by
>
> 1.  [Corey Schafer](https://github.com/CoreyMSchafer)’s [Python
>     YouTube API
>     tutorials](https://www.youtube.com/@coreyms/search?query=python%20youtube%20api%20tutorial),
>     and
> 2.  [Patrik Loeber](https://github.com/patrickloeber)’s [YouTube Data
>     API
>     tutorials](https://www.python-engineer.com/posts/youtube-data-api-01)
