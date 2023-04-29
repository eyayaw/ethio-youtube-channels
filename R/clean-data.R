library(data.table)

reNamer = function(x) {
    sub("(snippet|statistics|contentDetails|topicDetails)[.]", "", x)
}

channels_info = fread("data/channels-info.csv")
setnames(channels_info, reNamer)

files = dir("data", "^channels-data_\\d{2}-\\d{4}[.]csv$", full.names = TRUE)
channels_data = lapply(files, \(file) setnames(fread(file), reNamer))

# column id is missing in the first three months of 2023
channels_data = rbindlist(channels_data, use.names = TRUE, fill = TRUE)
channels_data[, id := fifelse(is.na(id), na.omit(id)[1], id), title]

channels_data = channels_info[, .(id, title, publishedAt, description)] |>
    merge(channels_data, by = c("id", "title"))
channels_data[, retrievedAt := as.POSIXct(retrievedAt, tz = "UTC")
                ][, publishedAt := as.POSIXct(publishedAt, tz = "UTC")]
# order by retrieved_at and id
setkey(channels_data, retrievedAt, id)

num_vars = c("viewCount", "subscriberCount", "videoCount")
channels_data[, (num_vars) := lapply(.SD, as.integer), .SDcols = (num_vars)]
setcolorder(channels_data, c("id", "title"))

# create new vars
channels_data[, viewCountPerVideo := floor(viewCount / videoCount)
                ][, age := round(as.numeric(retrievedAt - publishedAt)/365.25, 2)
                  ][, viewCountPerYear := floor(viewCount/age)]

# write all data into a csv
fwrite(channels_data, "data/processed/channels-data_merged.csv")