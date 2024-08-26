library(data.table)

lfiles = dir("data/old/", "[.]csv$", full.names = TRUE)

data = lapply(lfiles, fread, select = c("title", "viewCount", "subscriberCount", "videoCount"))
names(data) = sapply(strsplit(lfiles, "_"), `[`, 2) |>
  tools::file_path_sans_ext() |>
  {\(x) Map(\(t, z) as.POSIXct(t, z), substr(x, 1, 19), substr(x, 21, 23))}() |>
  unlist() |>
  as.POSIXct(tz="utc", origin="1970-01-01 00:00:00")


all_data = rbindlist(data, use.names = TRUE, idcol = "retrievedAt")
setcolorder(all_data, "title")

fwrite(all_data, "data/channels-data-utc.csv")


channels_data = fread("data/channels-data.csv")
channels_data[, retrievedAt := gsub("(2023-\\d{2}-\\d{2})T(\\d{2}:\\d{2}:\\d{2})Z", "\\1 \\2 UTC", retrievedAt)]
channels_data[, retrievedAt := gsub("(2022-\\d{2}-\\d{2})T(\\d{2}:\\d{2}:\\d{2})Z", "\\1 \\2 UTC", retrievedAt)]
channels_data[, retrievedAt := fcase(
    retrievedAt == "2023-01-08 00:09:16 UTC", "2023-01-07 23:03:16 UTC",
    retrievedAt == "2023-01-07 00:08:38 UTC", "2023-01-06 23:04:38 UTC",
    retrievedAt == "2023-01-06 00:08:36 UTC", "2023-01-05 23:08:36 UTC",
    retrievedAt == "2023-01-05 00:08:50 UTC", "2023-01-04 23:08:50 UTC",
    retrievedAt == "2023-01-04 08:50:54 UTC", "2023-01-03 23:50:54 UTC",
    retrievedAt == "2023-01-03 01:12:34 UTC", "2023-01-02 23:12:34 UTC",
    retrievedAt == "2023-01-01 16:17:23 UTC", "2023-01-01 23:17:23 UTC",
    rep_len(TRUE, length(retrievedAt)), retrievedAt)]


# view counts did not change on 2023-01-03 & 04
# we should correct for 2023-01-03 23:50:54 UTC because it was retrieved at
# 2023-01-04 08:50:54 UTC. When the github actions that supposed to run mid night
# fail, I sent a request when I woke up.
channels_data = fread("data/old/channels-data.csv")
channels_data[, retrievedAt := as.POSIXct(retrievedAt, "utc")]
setkey(channels_data, title, retrievedAt)
channels_data[, let(g = viewCount/shift(viewCount) - 1), title
              ][, day := format(retrievedAt, "%A")]

prob_date = as.POSIXct("2023-01-03 23:50:54 UTC", "utc")
prev_date = as.POSIXct("2023-01-02 23:12:34 UTC", "utc")
next_week_date = as.POSIXct("2023-01-10 23:04:54 UTC", "utc")

channels_data[, viewCount := fifelse(
  retrievedAt == prob_date,
  floor(viewCount[retrievedAt==prev_date] * (1+max(g[retrievedAt==next_week_date]))), viewCount), title]

channels_data[, let(day=NULL, g=NULL)]
setkey(channels_data, retrievedAt)
channels_data[, retrievedAt:=format(retrievedAt, "%F %T %Z")]

fwrite(channels_data, "data/channels-data.csv")
