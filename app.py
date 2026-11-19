
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# =========================
# PAGE CONFIGURATION
# =========================

st.set_page_config(
    page_title="Netflix Analytics Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# CUSTOM CSS
# =========================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background-color: #080b12;
        color: #f5f5f5;
    }

    [data-testid="stSidebar"] {
        background-color: #111620;
        border-right: 1px solid #252b38;
    }

    .main-header {
        font-size: 38px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 5px;
    }

    .main-header span {
        color: #e50914;
    }

    .sub-header {
        color: #9299a8;
        font-size: 14px;
        margin-bottom: 30px;
    }

    .section-title {
        font-size: 21px;
        font-weight: 700;
        color: #ffffff;
        margin-top: 25px;
        margin-bottom: 15px;
    }

    .metric-card {
        background: linear-gradient(145deg, #171e2b, #111620);
        border: 1px solid #292f3d;
        border-radius: 14px;
        padding: 22px;
        min-height: 125px;
    }

    .metric-label {
        color: #a0a7b5;
        font-size: 13px;
        font-weight: 500;
    }

    .metric-value {
        color: #ffffff;
        font-size: 30px;
        font-weight: 800;
        margin-top: 10px;
    }

    .metric-icon {
        font-size: 22px;
        float: right;
    }

    div[data-testid="stPlotlyChart"] {
        background: #111620;
        border: 1px solid #252b38;
        border-radius: 12px;
        padding: 10px;
    }

    .footer {
        text-align: center;
        color: #737b89;
        font-size: 12px;
        padding: 25px 0 10px 0;
        border-top: 1px solid #252b38;
        margin-top: 40px;
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid #252b38;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)


# =========================
# LOAD DATA
# =========================

@st.cache_data
def load_data():
    file_path = Path("data/netflix_titles.csv")

    if not file_path.exists():
        return None

    df = pd.read_csv(file_path)

    df.columns = df.columns.str.strip()

    if "date_added" in df.columns:
        df["date_added"] = pd.to_datetime(
            df["date_added"].astype(str).str.strip(),
            errors="coerce"
        )

    if "release_year" in df.columns:
        df["release_year"] = pd.to_numeric(
            df["release_year"], errors="coerce"
        )

    return df


df = load_data()

if df is None:
    st.error("Dataset not found! Check data/netflix_titles.csv")
    st.stop()

required_columns = [
    "type", "title", "country", "release_year",
    "listed_in", "rating", "duration"
]

missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    st.error(f"Missing required columns: {missing_columns}")
    st.stop()


# =========================
# SIDEBAR FILTERS
# =========================

st.sidebar.markdown(
    "<h2 style='color:#e50914;'>🎬 NETFLIX</h2>",
    unsafe_allow_html=True
)

st.sidebar.markdown("### Dashboard Filters")
st.sidebar.markdown("---")

content_types = ["All"] + sorted(
    df["type"].dropna().unique().tolist()
)

selected_type = st.sidebar.selectbox(
    "Content Type",
    content_types
)

years = df["release_year"].dropna()

if not years.empty:
    min_year = int(years.min())
    max_year = int(years.max())

    year_range = st.sidebar.slider(
        "Release Year",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year)
    )
else:
    year_range = (0, 9999)

countries = sorted({
    country.strip()
    for value in df["country"].dropna()
    for country in str(value).split(",")
    if country.strip()
})

selected_countries = st.sidebar.multiselect(
    "Countries",
    countries,
    placeholder="Select countries"
)

st.sidebar.markdown("---")
st.sidebar.caption("Netflix Content Analytics")
st.sidebar.caption("Data-driven insights into Netflix")


# =========================
# APPLY FILTERS
# =========================

filtered_df = df.copy()

if selected_type != "All":
    filtered_df = filtered_df[
        filtered_df["type"] == selected_type
    ]

filtered_df = filtered_df[
    filtered_df["release_year"].between(
        year_range[0], year_range[1]
    )
]

if selected_countries:
    filtered_df = filtered_df[
        filtered_df["country"].apply(
            lambda x: any(
                country.strip() in selected_countries
                for country in str(x).split(",")
            ) if pd.notna(x) else False
        )
    ]


# =========================
# HEADER
# =========================

st.markdown("""
<div class="main-header">
    NETFLIX <span>ANALYTICS</span>
</div>
<div class="sub-header">
    Explore Netflix's content library through data,
    trends and interactive visualizations.
</div>
""", unsafe_allow_html=True)


# =========================
# KPI METRICS
# =========================

total_titles = len(filtered_df)

total_movies = len(
    filtered_df[filtered_df["type"] == "Movie"]
)

total_shows = len(
    filtered_df[filtered_df["type"] == "TV Show"]
)

total_countries = len({
    country.strip()
    for value in filtered_df["country"].dropna()
    for country in str(value).split(",")
    if country.strip()
})


def metric_card(label, value, icon):
    st.markdown(f"""
    <div class="metric-card">
        <span class="metric-icon">{icon}</span>
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value:,}</div>
    </div>
    """, unsafe_allow_html=True)


col1, col2, col3, col4 = st.columns(4)

with col1:
    metric_card("TOTAL TITLES", total_titles, "🎬")

with col2:
    metric_card("MOVIES", total_movies, "🍿")

with col3:
    metric_card("TV SHOWS", total_shows, "📺")

with col4:
    metric_card("COUNTRIES", total_countries, "🌍")


if filtered_df.empty:
    st.warning("No titles found for the selected filters.")
    st.stop()


# =========================
# CONTENT DISTRIBUTION
# =========================

st.markdown(
    '<div class="section-title">📊 Content Overview</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:
    type_data = (
        filtered_df["type"]
        .value_counts()
        .reset_index()
    )
    type_data.columns = ["Type", "Count"]

    fig = px.pie(
        type_data,
        names="Type",
        values="Count",
        hole=0.65,
        color="Type",
        color_discrete_map={
            "Movie": "#E50914",
            "TV Show": "#F5A623"
        }
    )

    fig.update_traces(
        textinfo="label+percent",
        textfont_size=12
    )

    fig.update_layout(
        title="Movies vs TV Shows",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#ffffff",
        margin=dict(t=55, b=20, l=20, r=20),
        legend_title_text=""
    )

    st.plotly_chart(fig, use_container_width=True)


with col2:
    year_data = (
        filtered_df.dropna(subset=["release_year"])
        .groupby("release_year")
        .size()
        .reset_index(name="Total Titles")
    )

    fig = px.area(
        year_data,
        x="release_year",
        y="Total Titles",
        title="Content Released Over the Years",
        color_discrete_sequence=["#E50914"]
    )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#ffffff",
        xaxis_title="Release Year",
        yaxis_title="Number of Titles",
        margin=dict(t=55, b=30, l=20, r=20)
    )

    st.plotly_chart(fig, use_container_width=True)


# =========================
# GENRE ANALYSIS
# =========================

st.markdown(
    '<div class="section-title">🎭 Genre Analysis</div>',
    unsafe_allow_html=True
)

genre_data = (
    filtered_df["listed_in"]
    .dropna()
    .str.split(",")
    .explode()
    .str.strip()
)

genre_counts = (
    genre_data.value_counts()
    .head(10)
    .sort_values()
    .reset_index()
)

genre_counts.columns = ["Genre", "Count"]

fig = px.bar(
    genre_counts,
    x="Count",
    y="Genre",
    orientation="h",
    text="Count",
    color="Count",
    color_continuous_scale=["#7a1118", "#E50914"]
)

fig.update_layout(
    title="Top 10 Popular Genres",
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#ffffff",
    coloraxis_showscale=False,
    xaxis_title="Number of Titles",
    yaxis_title="",
    margin=dict(t=55, b=25, l=20, r=20)
)

st.plotly_chart(fig, use_container_width=True)


# =========================
# COUNTRY ANALYSIS
# =========================

st.markdown(
    '<div class="section-title">🌍 Global Content Distribution</div>',
    unsafe_allow_html=True
)

country_data = (
    filtered_df["country"]
    .dropna()
    .str.split(",")
    .explode()
    .str.strip()
)

country_counts = (
    country_data.value_counts()
    .head(10)
    .sort_values()
    .reset_index()
)

country_counts.columns = ["Country", "Titles"]

fig = px.bar(
    country_counts,
    x="Titles",
    y="Country",
    orientation="h",
    text="Titles",
    color="Titles",
    color_continuous_scale=["#7a1118", "#E50914"]
)

fig.update_layout(
    title="Top 10 Content Producing Countries",
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#ffffff",
    coloraxis_showscale=False,
    xaxis_title="Number of Titles",
    yaxis_title="",
    margin=dict(t=55, b=25, l=20, r=20)
)

st.plotly_chart(fig, use_container_width=True)


# =========================
# CONTENT EXPLORER
# =========================

st.markdown(
    '<div class="section-title">🔎 Explore Netflix Titles</div>',
    unsafe_allow_html=True
)

search_query = st.text_input(
    "Search for a movie or TV show",
    placeholder="Enter a title..."
)

explorer_df = filtered_df.copy()

if search_query:
    explorer_df = explorer_df[
        explorer_df["title"].str.contains(
            search_query,
            case=False,
            na=False
        )
    ]

display_columns = [
    col for col in [
        "title", "type", "release_year",
        "rating", "duration", "country", "listed_in"
    ]
    if col in explorer_df.columns
]

st.dataframe(
    explorer_df[display_columns].reset_index(drop=True),
    use_container_width=True,
    hide_index=True
)

st.caption(
    f"Showing {len(explorer_df):,} titles | "
    f"{len(filtered_df):,} titles after filters"
)


# =========================
# FOOTER
# =========================

st.markdown("""
<div class="footer">
    NETFLIX DATA ANALYSIS DASHBOARD
    <br><br>
    Built with Python · Streamlit · Pandas · Plotly
</div>
""", unsafe_allow_html=True)
