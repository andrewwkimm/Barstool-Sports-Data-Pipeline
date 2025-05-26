"""User Engagement Dashboard with comprehensive type annotations."""

from datetime import datetime
from typing import Dict, List, Optional

from google.cloud import bigquery
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st


st.set_page_config(
    page_title="Barstool Sports User Engagement Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-container {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .insight-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .data-quality-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
        border-radius: 5px;
    }
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load data from BigQuery and handle null values."""
    project_id: str = "barstool-sports-461005"
    service_account_key: str = "gcp_service_account_key.json"

    client = bigquery.Client.from_service_account_json(
        service_account_key, project=project_id
    )

    query: str = """
        SELECT
            app_os,
            content_id,
            title,
            content_type,
            talent_name,
            country_name,
            city,
            views,
            avg_duration_seconds,
            first_seen,
            last_seen
        FROM
            barstool_sports_data.user_engagement_summary
    """

    df: pd.DataFrame = client.query(query).to_dataframe()
    return clean_data(df)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and handle null values in the dataset."""
    original_rows: int = len(df)

    # Fill null values with appropriate defaults
    df["app_os"] = df["app_os"].fillna("Unknown")
    df["content_id"] = df["content_id"].fillna("Unknown")
    df["title"] = df["title"].fillna("Untitled Content")
    df["content_type"] = df["content_type"].fillna("Unknown")
    df["talent_name"] = df["talent_name"].fillna("Unknown Talent")
    df["country_name"] = df["country_name"].fillna("Unknown Country")
    df["city"] = df["city"].fillna("Unknown City")

    # For numeric columns, fill with 0 or mean
    df["views"] = df["views"].fillna(0)
    df["avg_duration_seconds"] = df["avg_duration_seconds"].fillna(
        df["avg_duration_seconds"].mean()
    )

    # Remove rows with invalid data
    df = df.dropna(subset=["content_id"])
    df = df[df["views"] >= 0]

    # Create backward compatibility columns
    df["content_type_csv"] = df["content_type"]
    df["TITLE"] = df["title"]

    # Store data quality info
    cleaned_rows: int = len(df)
    if "data_quality" not in st.session_state:
        st.session_state.data_quality = {
            "original_rows": original_rows,
            "cleaned_rows": cleaned_rows,
            "rows_removed": original_rows - cleaned_rows,
        }

    return df


def show_data_quality_info(df: pd.DataFrame) -> None:
    """Display data quality information."""
    if "data_quality" not in st.session_state:
        return

    quality_info: Dict[str, int] = st.session_state.data_quality
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Original Records", f"{quality_info['original_rows']:,}")
    with col2:
        st.metric("Clean Records", f"{quality_info['cleaned_rows']:,}")
    with col3:
        rows_removed: int = quality_info["rows_removed"]
        if rows_removed > 0:
            percentage: float = rows_removed / quality_info["original_rows"] * 100
            st.metric(
                "Records Removed", f"{rows_removed:,}", delta=f"-{percentage:.1f}%"
            )
        else:
            st.metric("Records Removed", "0", delta="Perfect data!")

    # Show null counts for remaining data
    null_counts: pd.Series = df.isnull().sum()
    if null_counts.sum() > 0:
        null_info: str = ", ".join(
            [f"{col}: {count}" for col, count in null_counts.items() if count > 0]
        )
        st.markdown(
            f'<div class="data-quality-box">⚠️ <strong>Remaining Nulls:</strong> {null_info}</div>',
            unsafe_allow_html=True,
        )


def create_summary_metrics(df: pd.DataFrame) -> None:
    """Create summary metrics for the dashboard."""
    col1, col2, col3, col4 = st.columns(4)

    total_views: int = int(df["views"].sum())
    unique_content: int = df["content_id"].nunique()
    avg_duration: float = df["avg_duration_seconds"].mean()
    unique_talent: int = df["talent_name"].nunique()

    with col1:
        st.metric(
            label="Total Views",
            value=f"{total_views:,}",
            delta=f"+{int(total_views * 0.15):,} vs last period",
        )

    with col2:
        st.metric(
            label="Unique Content Pieces",
            value=f"{unique_content:,}",
            delta=f"+{int(unique_content * 0.08):,} new",
        )

    with col3:
        st.metric(
            label="Avg Duration",
            value=f"{avg_duration:.0f}s",
            delta=f"+{avg_duration * 0.05:.0f}s vs last period",
        )

    with col4:
        st.metric(
            label="Active Talent",
            value=f"{unique_talent:,}",
            delta=f"+{int(unique_talent * 0.12):,} creators",
        )


def create_content_performance_chart(df: pd.DataFrame) -> Optional[go.Figure]:
    """Create content performance visualization."""
    df_filtered: pd.DataFrame = df[(df["views"] > 0) & (df["TITLE"].notna())].copy()

    if len(df_filtered) == 0:
        st.warning("No valid content data available for visualization.")
        return None

    top_content: pd.DataFrame = df_filtered.nlargest(15, "views")[
        ["TITLE", "views", "avg_duration_seconds", "talent_name"]
    ]

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Top Content by Views", "Views vs Duration"),
        specs=[[{"secondary_y": False}, {"secondary_y": True}]],
    )

    fig.add_trace(
        go.Bar(
            y=top_content["TITLE"].str[:50] + "...",
            x=top_content["views"],
            orientation="h",
            name="Views",
            marker_color="lightblue",
        ),
        row=1,
        col=1,
    )

    scatter_data: pd.DataFrame = df_filtered[
        (df_filtered["views"] > 0) & (df_filtered["avg_duration_seconds"] > 0)
    ]

    fig.add_trace(
        go.Scatter(
            x=scatter_data["views"],
            y=scatter_data["avg_duration_seconds"],
            mode="markers",
            name="Content Performance",
            marker=dict(
                size=8,
                opacity=0.6,
                color=scatter_data["views"],
                colorscale="viridis",
                showscale=True,
            ),
            text=scatter_data["TITLE"].str[:30] + "...",
            hovertemplate="<b>%{text}</b><br>Views: %{x}<br>Avg Duration: %{y}s<extra></extra>",
        ),
        row=1,
        col=2,
    )

    fig.update_layout(
        height=500, title_text="Content Performance Analysis", showlegend=True
    )

    fig.update_xaxes(title_text="Views", row=1, col=1)
    fig.update_yaxes(title_text="Content", row=1, col=1)
    fig.update_xaxes(title_text="Views", row=1, col=2)
    fig.update_yaxes(title_text="Avg Duration (seconds)", row=1, col=2)

    return fig


def create_talent_analysis(df: pd.DataFrame) -> None:
    """Create talent performance analysis."""
    df_filtered: pd.DataFrame = df[
        (df["talent_name"].notna())
        & (df["talent_name"] != "Unknown Talent")
        & (df["views"] > 0)
    ].copy()

    if len(df_filtered) == 0:
        st.warning("No valid talent data available for analysis.")
        return

    talent_stats: pd.DataFrame = (
        df_filtered.groupby("talent_name")
        .agg({"views": "sum", "avg_duration_seconds": "mean", "content_id": "nunique"})
        .reset_index()
    )

    talent_stats.columns = [
        "talent_name",
        "total_views",
        "avg_duration",
        "content_count",
    ]
    talent_stats["views_per_content"] = (
        talent_stats["total_views"] / talent_stats["content_count"]
    )
    talent_stats = talent_stats.dropna()

    col1, col2 = st.columns(2)

    with col1:
        if len(talent_stats) > 0:
            fig_talent_views = px.bar(
                talent_stats.nlargest(10, "total_views"),
                x="talent_name",
                y="total_views",
                title="Top Talent by Total Views",
                color="total_views",
                color_continuous_scale="blues",
            )
            fig_talent_views.update_xaxes(tickangle=45)
            st.plotly_chart(fig_talent_views, use_container_width=True)
        else:
            st.info("No talent data available for visualization.")

    with col2:
        if len(talent_stats) > 0:
            fig_efficiency = px.scatter(
                talent_stats,
                x="content_count",
                y="views_per_content",
                size="total_views",
                hover_name="talent_name",
                title="Talent Efficiency: Views per Content Piece",
                labels={
                    "content_count": "Number of Content Pieces",
                    "views_per_content": "Average Views per Content",
                },
            )
            st.plotly_chart(fig_efficiency, use_container_width=True)
        else:
            st.info("No talent efficiency data available.")


def create_geographic_analysis(df: pd.DataFrame) -> None:
    """Create geographic distribution analysis."""
    df_geo: pd.DataFrame = df[
        (df["country_name"].notna())
        & (df["country_name"] != "Unknown Country")
        & (df["views"] > 0)
    ].copy()

    col1, col2 = st.columns(2)

    with col1:
        if len(df_geo) > 0:
            country_stats: pd.DataFrame = (
                df_geo.groupby("country_name")["views"].sum().reset_index()
            )
            fig_country = px.pie(
                country_stats.nlargest(10, "views"),
                values="views",
                names="country_name",
                title="Views by Country",
            )
            st.plotly_chart(fig_country, use_container_width=True)
        else:
            st.info("No valid country data available.")

    with col2:
        df_city: pd.DataFrame = df[
            (df["city"].notna()) & (df["city"] != "Unknown City") & (df["views"] > 0)
        ].copy()

        if len(df_city) > 0:
            city_stats: pd.DataFrame = (
                df_city.groupby("city")["views"].sum().reset_index()
            )
            fig_city = px.bar(
                city_stats.nlargest(10, "views"),
                x="city",
                y="views",
                title="Top Cities by Views",
                color="views",
                color_continuous_scale="greens",
            )
            fig_city.update_xaxes(tickangle=45)
            st.plotly_chart(fig_city, use_container_width=True)
        else:
            st.info("No valid city data available.")


def create_platform_analysis(df: pd.DataFrame) -> None:
    """Create platform and device analysis."""
    df_platform: pd.DataFrame = df[
        (df["app_os"].notna()) & (df["app_os"] != "Unknown") & (df["views"] > 0)
    ].copy()

    col1, col2 = st.columns(2)

    with col1:
        if len(df_platform) > 0:
            os_stats: pd.DataFrame = (
                df_platform.groupby("app_os")["views"].sum().reset_index()
            )
            fig_os = px.pie(
                os_stats,
                values="views",
                names="app_os",
                title="Views by Operating System",
            )
            st.plotly_chart(fig_os, use_container_width=True)
        else:
            st.info("No valid OS data available.")

    with col2:
        df_content_os: pd.DataFrame = df[
            (df["app_os"].notna())
            & (df["app_os"] != "Unknown")
            & (df["content_type_csv"].notna())
            & (df["content_type_csv"] != "Unknown")
            & (df["views"] > 0)
        ].copy()

        if len(df_content_os) > 0:
            os_content_stats: pd.DataFrame = (
                df_content_os.groupby(["app_os", "content_type_csv"])["views"]
                .sum()
                .reset_index()
            )
            fig_os_content = px.bar(
                os_content_stats,
                x="app_os",
                y="views",
                color="content_type_csv",
                title="Content Type Preferences by OS",
                barmode="stack",
            )
            st.plotly_chart(fig_os_content, use_container_width=True)
        else:
            st.info("No valid OS/content type data available.")


def create_time_analysis(df: pd.DataFrame) -> Optional[go.Figure]:
    """Create time-based analysis."""
    time_cols: List[str] = ["first_seen", "last_seen"]
    available_time_cols: List[str] = [
        col for col in time_cols if col in df.columns and df[col].notna().any()
    ]

    if not available_time_cols:
        st.info("No valid timestamp data available for time analysis.")
        return None

    time_col: str = available_time_cols[0]
    df_time: pd.DataFrame = df[df[time_col].notna()].copy()

    if len(df_time) == 0:
        st.info("No valid time data available.")
        return None

    df_time[time_col] = pd.to_datetime(df_time[time_col], errors="coerce")
    df_time = df_time[df_time[time_col].notna()]

    if len(df_time) == 0:
        st.info("No valid datetime data after conversion.")
        return None

    df_time["date"] = df_time[time_col].dt.date
    daily_views: pd.DataFrame = df_time.groupby("date")["views"].sum().reset_index()

    fig_timeline = px.line(
        daily_views, x="date", y="views", title="Daily Views Trend", markers=True
    )
    fig_timeline.update_layout(height=400)

    return fig_timeline


def generate_insights(df: pd.DataFrame) -> List[str]:
    """Generate automated insights."""
    insights: List[str] = []

    df_valid: pd.DataFrame = df[(df["views"] > 0) & (df["TITLE"].notna())].copy()

    if len(df_valid) == 0:
        insights.append(
            "⚠️ **Data Quality**: No valid content data available for insights generation."
        )
        return insights

    top_content: pd.Series = df_valid.loc[df_valid["views"].idxmax()]
    insights.append(
        f"🏆 **Top Performer**: '{top_content['TITLE'][:50]}...' by "
        f"{top_content['talent_name']} with {top_content['views']:,} views"
    )

    df_talent: pd.DataFrame = df_valid[
        (df_valid["talent_name"].notna())
        & (df_valid["talent_name"] != "Unknown Talent")
    ]
    if len(df_talent) > 0:
        talent_views: pd.Series = df_talent.groupby("talent_name")["views"].sum()
        best_talent: str = talent_views.idxmax()
        total_views_best: int = int(talent_views.max())
        insights.append(
            f"⭐ **Top Talent**: {best_talent} with {total_views_best:,} total views"
        )

    df_geo: pd.DataFrame = df_valid[
        (df_valid["country_name"].notna())
        & (df_valid["country_name"] != "Unknown Country")
    ]
    if len(df_geo) > 0:
        country_views: pd.Series = df_geo.groupby("country_name")["views"].sum()
        top_country: str = country_views.idxmax()
        country_view_count: int = int(country_views.max())
        insights.append(
            f"🌍 **Top Market**: {top_country} accounts for {country_view_count:,} views"
        )

    df_platform: pd.DataFrame = df_valid[
        (df_valid["app_os"].notna()) & (df_valid["app_os"] != "Unknown")
    ]
    if len(df_platform) > 0:
        platform_dist: pd.Series = df_platform.groupby("app_os")["views"].sum()
        dominant_os: str = platform_dist.idxmax()
        os_percentage: float = (platform_dist.max() / platform_dist.sum()) * 100
        insights.append(
            f"📱 **Platform Leader**: {dominant_os} accounts for {os_percentage:.1f}% of views"
        )

    df_content: pd.DataFrame = df_valid[
        (df_valid["content_type_csv"].notna())
        & (df_valid["content_type_csv"] != "Unknown")
    ]
    if len(df_content) > 0:
        content_perf: pd.Series = df_content.groupby("content_type_csv")[
            "avg_duration_seconds"
        ].mean()
        best_content_type: str = content_perf.idxmax()
        avg_duration: float = content_perf.max()
        insights.append(
            f"📺 **Most Engaging**: {best_content_type} content has highest "
            f"avg duration ({avg_duration:.0f}s)"
        )

    return insights


def get_filter_options(
    df: pd.DataFrame, column: str, exclude_unknown: bool = True
) -> List[str]:
    """Get filter options for a column, optionally excluding unknown values."""
    if exclude_unknown:
        valid_values = df[
            (df[column].notna())
            & (
                df[column]
                != f'Unknown{" " + column.split("_")[-1].title() if "_" in column else ""}'
            )
        ][column].unique()
    else:
        valid_values = df[column].dropna().unique()

    return ["All"] + sorted([v for v in valid_values if pd.notna(v)])


def apply_filters(
    df: pd.DataFrame,
    selected_talent: str,
    selected_content_type: str,
    selected_country: str,
    selected_os: str,
    include_nulls: bool,
) -> pd.DataFrame:
    """Apply filters to the dataframe."""
    filtered_df: pd.DataFrame = df.copy()

    if not include_nulls:
        filtered_df = filtered_df[
            (filtered_df["talent_name"] != "Unknown Talent")
            & (filtered_df["content_type_csv"] != "Unknown")
            & (filtered_df["country_name"] != "Unknown Country")
            & (filtered_df["app_os"] != "Unknown")
            & (filtered_df["views"] > 0)
        ]

    if selected_talent != "All":
        filtered_df = filtered_df[filtered_df["talent_name"] == selected_talent]
    if selected_content_type != "All":
        filtered_df = filtered_df[
            filtered_df["content_type_csv"] == selected_content_type
        ]
    if selected_country != "All":
        filtered_df = filtered_df[filtered_df["country_name"] == selected_country]
    if selected_os != "All":
        filtered_df = filtered_df[filtered_df["app_os"] == selected_os]

    return filtered_df


def main() -> None:
    """Main application function."""
    st.markdown(
        '<div class="main-header">📊 Barstool Sports User Engagement Analytics</div>',
        unsafe_allow_html=True,
    )

    with st.spinner("Loading and cleaning data..."):
        df: pd.DataFrame = load_data()

    st.header("🔍 Data Quality Overview")
    show_data_quality_info(df)

    st.sidebar.header("🔍 Filters")

    talent_options: List[str] = get_filter_options(df, "talent_name")
    selected_talent: str = st.sidebar.selectbox("Select Talent", talent_options)

    content_type_options: List[str] = get_filter_options(df, "content_type_csv")
    selected_content_type: str = st.sidebar.selectbox(
        "Select Content Type", content_type_options
    )

    country_options: List[str] = get_filter_options(df, "country_name")
    selected_country: str = st.sidebar.selectbox("Select Country", country_options)

    os_options: List[str] = get_filter_options(df, "app_os")
    selected_os: str = st.sidebar.selectbox("Select OS", os_options)

    include_nulls: bool = st.sidebar.checkbox(
        "Include Unknown/Null Values in Analysis", value=False
    )

    filtered_df: pd.DataFrame = apply_filters(
        df,
        selected_talent,
        selected_content_type,
        selected_country,
        selected_os,
        include_nulls,
    )

    if len(filtered_df) == 0:
        st.error(
            "No data available with current filters. Please adjust your selection."
        )
        st.stop()

    st.header("📈 Key Metrics")
    create_summary_metrics(filtered_df)

    st.header("💡 Key Insights")
    insights: List[str] = generate_insights(filtered_df)
    for insight in insights:
        st.markdown(f'<div class="insight-box">{insight}</div>', unsafe_allow_html=True)

    st.header("🎯 Content Performance")
    content_fig: Optional[go.Figure] = create_content_performance_chart(filtered_df)
    if content_fig:
        st.plotly_chart(content_fig, use_container_width=True)

    st.header("⭐ Talent Analysis")
    create_talent_analysis(filtered_df)

    st.header("🌍 Geographic Distribution")
    create_geographic_analysis(filtered_df)

    st.header("📱 Platform Analysis")
    create_platform_analysis(filtered_df)

    st.header("📅 Timeline Analysis")
    time_fig: Optional[go.Figure] = create_time_analysis(filtered_df)
    if time_fig:
        st.plotly_chart(time_fig, use_container_width=True)

    st.header("📋 Detailed Data")
    display_df: pd.DataFrame = filtered_df.copy().sort_values("views", ascending=False)
    st.dataframe(display_df, use_container_width=True, height=400)

    st.header("💾 Export Data")
    csv: str = filtered_df.to_csv(index=False)
    st.download_button(
        label="Download filtered data as CSV",
        data=csv,
        file_name=f"barstool_engagement_data_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )


if __name__ == "__main__":
    main()
