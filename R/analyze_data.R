library(data.table)
library(ggplot2)
library(ggtext)

data = fread("./channels-data_merged.csv")
caption_text = "Data: accessed via <span style = 'color:red;'>YouTube Data API v3</span><br>Author: <span style = 'color:#0090e8;'>github.com/eyayaw</span>"

make_ts_plot <- function(data, channel_id, y, ...) {
  data |>
  subset(id == channel_id) |>
    ggplot(aes(retrievedAt, {{y}})) +
    geom_point() +
    geom_line() +
    labs(x = "Date", caption = caption_text, title = data[id == channel_id, title[[1]]]) +
    theme_light() +
    theme(
      plot.caption = element_markdown(face = "italic"),
      plot.title = element_text(hjust = .5)
    )
}

# subscriber count
data |> (\(x)
make_ts_plot(x, 'UCvr6jA3WYOhXFUD2LKpqhQw', subscriberCount) +
  geom_hline(yintercept = 600000L, lty = 2, color = "red") +
  scale_y_continuous(breaks = c(seq(5, 6, .25) * 1e+5, max(x$subscriberCount))) +
  ggtitle("Ethio 360 Media Subscriber Count 2023")
)()

# view count
data[order(retrievedAt),
    ][, .(retrievedAt, title, viewCount = viewCount - shift(viewCount)), id] |>
  make_ts_plot("UCvr6jA3WYOhXFUD2LKpqhQw", abs(viewCount)) +
  scale_y_continuous(labels = scales::label_number(scale = 1e-3))
