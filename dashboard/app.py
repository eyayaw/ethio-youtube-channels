import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
import matplotlib.dates as mdates
import seaborn as sns

# Path to your data
DATA_PATH = os.path.join('data', 'processed', 'channels-data_merged.csv')

st.set_page_config(page_title='Ethiopian YouTube Channels Dashboard', layout='wide')
st.title('Ethiopian YouTube Channels Dashboard')

# Set a modern style for matplotlib
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette('Set2')

# Cache data loading for faster interaction
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(DATA_PATH)
        return df
    except Exception as e:
        st.error(f'Error loading data: {e}')
        return None

df = load_data()
if df is None:
    st.warning('No data to display.')
    st.stop()

st.write('### Raw Data Preview')
st.dataframe(df.head())

# Explicitly set your columns
channel_col = 'title'
date_col = 'retrievedAt'

# Parse dates
df[date_col] = pd.to_datetime(df[date_col], errors='coerce')

# Metrics to choose from
available_metrics = [
    'subscriberCount', 'viewCount', 'videoCount', 'viewCountPerVideo', 'viewCountPerYear'
]

metric = st.selectbox('Select metric to plot', available_metrics, index=0)

# Search/filter for channels
with st.sidebar:
    st.header("Channel Filter")
    search_query = st.text_input('Search channels (partial name allowed):')
    all_channels = sorted(df[channel_col].dropna().unique())
    if search_query:
        filtered_channels = [ch for ch in all_channels if search_query.lower() in ch.lower()]
    else:
        filtered_channels = all_channels

    if not filtered_channels:
        st.error('No channels match your search.')
        st.stop()

    st.write(f"Channels matching search: {len(filtered_channels)} of {len(all_channels)} total.")

    # Limit default selection to up to 10 channels
    default_selection = filtered_channels[:10]

    selected_channels = st.multiselect(
        'Select channels to plot (max 10 pre-selected)',
        options=filtered_channels,
        default=default_selection
    )

if not selected_channels:
    st.warning('No channels selected.')
    st.stop()

plot_df = df[df[channel_col].isin(selected_channels)].copy()

# Date range selection
min_date, max_date = plot_df[date_col].min(), plot_df[date_col].max()

if pd.isna(min_date) or pd.isna(max_date):
    st.error("No valid dates found in your filtered data. Cannot create date slider.")
    st.stop()

# Convert pandas Timestamps to native Python datetime.datetime for st.slider
min_date = min_date.to_pydatetime()
max_date = max_date.to_pydatetime()

date_range = st.slider(
    "Select date range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date),
    format="YYYY-MM-DD"
)

filtered_df = plot_df[
    (plot_df[date_col] >= pd.to_datetime(date_range[0])) &
    (plot_df[date_col] <= pd.to_datetime(date_range[1]))
].sort_values(date_col)

if filtered_df.empty:
    st.error('No data available in the selected date range.')
    st.stop()

# Summary statistics
st.write(f"## Summary Statistics for Selected Channels ({metric})")
summary_df = (
    filtered_df.groupby(channel_col)[metric]
    .agg(['min', 'max', 'mean', 'std'])
    .round(2)
    .reset_index()
)
st.dataframe(summary_df)

# Optional log scale
use_log = st.checkbox('Log scale y-axis')

# Plot with matplotlib
pivot_df = filtered_df.pivot(index=date_col, columns=channel_col, values=metric)[selected_channels]

fig, ax = plt.subplots(figsize=(14, 7))

# Plot each channel with a distinct color and marker
for i, ch in enumerate(selected_channels):
    ax.plot(
        pivot_df.index,
        pivot_df[ch],
        label=ch,
        marker='o',
        linewidth=2,
        markersize=5,
        alpha=0.85
    )

# Improve x-axis formatting
ax.xaxis.set_major_locator(mdates.AutoDateLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
fig.autofmt_xdate(rotation=30)

ax.set_xlabel('Date', fontsize=13, fontweight='bold')
ax.set_ylabel(metric, fontsize=13, fontweight='bold')
ax.set_title(f'{metric} Over Time', fontsize=16, fontweight='bold', pad=15)
ax.grid(True, which='major', linestyle='--', linewidth=0.5, alpha=0.7)
ax.legend(title='Channel', loc='upper left', fontsize=11, title_fontsize=12, frameon=True)

if use_log:
    ax.set_yscale('log')

sns.despine()
st.pyplot(fig, use_container_width=True)

# Channel profile cards
st.write("## Channel Profiles")
for ch in selected_channels:
    ch_df = filtered_df[filtered_df[channel_col] == ch].sort_values(date_col)
    if not ch_df.empty:
        latest = ch_df.iloc[-1]
        st.markdown(f"### {ch}")
        st.write(f"**Latest Date:** {latest[date_col].date()}")
        st.write(f"**Subscribers:** {latest.get('subscriberCount', 'N/A'):,}")
        st.write(f"**Views:** {latest.get('viewCount', 'N/A'):,}")
        st.write(f"**Videos:** {latest.get('videoCount', 'N/A'):,}")