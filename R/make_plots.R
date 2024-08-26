library(ggplot2)
library(ggtext)

# flipped labelled bar plot ----
bar_plot <-
  function(data, x, y, label, geom.col.params = list(), geom.text.params = list()) {
    geom.col.params <- modifyList(list(fill = "#55bdb4", alpha = .5, width = .8), geom.col.params)
    geom.text.params <- modifyList(
      list(mapping = aes(label = {{ label }}, hjust = ifelse({{ x }} == max({{ x }}), 1L, -0.05))),
      geom.text.params
    )
    ggplot(data = data, mapping = aes({{ x }}, y = reorder({{ y }}, {{ x }}))) +
      do.call("geom_col", geom.col.params) +
      do.call("geom_text", geom.text.params) +
      scale_x_continuous(expand = expansion(mult = c(0, .1))) +
      ylab(NULL) +
      theme(
        plot.title = element_text(size = rel(1.1), face = "bold", hjust = 0.5),
        plot.caption = element_markdown(),
        axis.text = element_text(size = rel(.9)),
        panel.grid.major.y = element_blank(),
        panel.grid.minor = element_blank(),
        plot.background = element_rect(fill = "gray99", color = NA)
      )
  }

# individual channel chart

ch_plot <- function(data, channel_name_regex) {
  varying = c("viewCount", "subscriberCount", "videoCount")
  idvar = c("id", "title", "publishedAt", "description", "retrievedAt")
  subset(data, subset = grepl(channel_name_regex, title, ignore.case = TRUE)) |>
    reshape(
      direction = "long", varying = varying, idvar = idvar,
      v.names = "value", timevar = "variable"
    ) |>
    ggplot() +
    geom_line(aes(retrievedAt, value, color = variable)) +
    facet_wrap(~variable, scales = "free_y") +
    scale_x_date(labels = "%F")
}
