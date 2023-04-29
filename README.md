
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

| id                                                                                     | statistics.viewCount | statistics.subscriberCount | statistics.videoCount |
|:---------------------------------------------------------------------------------------|---------------------:|---------------------------:|----------------------:|
| [Abebe Belew](https://youtube.com/channel/UCxIn6j4tH1dVnqLd1WFvFNA)                    |             30303247 |                     152000 |                  1062 |
| [Adebabay Media](https://youtube.com/channel/UC-kDmfnktrzc_SGpS9ulrXw)                 |             13036893 |                      99400 |                   914 |
| [Alpha Media አልፋ ሚዲያ](https://youtube.com/channel/UCUyDe7EvbwwDRjyjUFU5Zhw)            |              5411148 |                      40400 |                   981 |
| [Anchor Ethiopia](https://youtube.com/channel/UCgIxJwBNuGzDKrBaZhATDug)                |              6648079 |                      80400 |                   236 |
| [Andafta](https://youtube.com/channel/UCwMHDoJO6cHO6LN1BItFsPQ)                        |            269542794 |                     889000 |                  5974 |
| [Arat Kilo Media አራት ኪሎ ሚዲያ](https://youtube.com/channel/UCK71ZGx5VYTWw2XQ0F_O0nQ)     |               669293 |                      16100 |                    89 |
| [Ashara Media - አሻራ ሚዲያ](https://youtube.com/channel/UCPmgFzP2ZPmdGjHxXjigJaw)         |              2971184 |                      35100 |                   771 |
| [EMS (Ethiopian Media Services)](https://youtube.com/channel/UCCJbY4YdJIUk7Lygrkg5IRA) |             44514734 |                     222000 |                  1046 |
| [ESATtv Ethiopia](https://youtube.com/channel/UCSYM-vgRrMYsZbG-Z7Kz0Pw)                |            197405901 |                     641000 |                  8811 |
| [ETHIO 251 MEDIA](https://youtube.com/channel/UCUOJQ0kAEqms79eY37hH-Jg)                |             13187078 |                     109000 |                   912 |
| [Ethio 360 Media](https://youtube.com/channel/UCvr6jA3WYOhXFUD2LKpqhQw)                |            230124604 |                     583000 |                  4006 |
| [Ethio News - ኢትዮ ኒውስ](https://youtube.com/channel/UCelbYFUaQW3eb9sg3004ZGw)           |             29028481 |                     164000 |                  1430 |
| [EthioTube](https://youtube.com/channel/UCCk2vUhB0SyQhA6JXyjXHEg)                      |             40330479 |                     224000 |                  1750 |
| [Feta Daily News](https://youtube.com/channel/UCgBnBckSLo6-uAiejtnEycQ)                |            149028357 |                     583000 |                   991 |
| [GEBEYANU](https://youtube.com/channel/UCb9fEB6StrknyRiSSzQ7H0A)                       |             10266427 |                     107000 |                   638 |
| [MENELIK TELEVISION 3](https://youtube.com/channel/UC-jwtt0RVJPNidr2Ja1_7yQ)           |               246145 |                       2910 |                   129 |
| [Mager Media - ማገር](https://youtube.com/channel/UCilWrw2C8_VkFZ2tE5eKpdQ)              |              1213374 |                      22900 |                   322 |
| [Mengizem Media ምንጊዜም ሚዲያ](https://youtube.com/channel/UCZvMKrP8XmP9GAHMloucOaA)       |              3660557 |                      31200 |                  1296 |
| [OMN](https://youtube.com/channel/UCmAnzjcjIgtWuE6AnBCViTg)                            |            110513467 |                     513000 |                  9670 |
| [Reyot](https://youtube.com/channel/UCPVr1rrKl8pXVFi-rrqzS1g)                          |             43204588 |                     189000 |                  2069 |
| [Roha](https://youtube.com/channel/UCDXU7RuIQc0xRKJyP0ZTZaQ)                           |             11563335 |                      95200 |                   975 |
| [Terara Network](https://youtube.com/channel/UC_f89AbX5NPU77YaoaSKRSg)                 |              3389884 |                      45100 |                   276 |
| [Tigrai Media House](https://youtube.com/channel/UCBvvcSYeDriczyImdI1qZWw)             |            155145214 |                     351000 |                  5473 |
| [Zara Media Network - ዛራ](https://youtube.com/channel/UCJ61rOk0c0b0COn0qOOo1aQ)        |             21515125 |                     129000 |                   418 |
| [ኢትዮ ሰላም Ethio Selam](https://youtube.com/channel/UCoVL5YOr2KdnYNspQf3s5uw)            |              3032904 |                      37700 |                   120 |
| [ዓባይ ዜና - Abbay News](https://youtube.com/channel/UC6bam4pQbuUgXnmyEFlSpNA)            |             17843758 |                     335000 |                  1182 |

Snapshot of stats as of 2023-04-01 23:04:33

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

4.  Install Quarto and use it to render the  chart.qmd  file.

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
