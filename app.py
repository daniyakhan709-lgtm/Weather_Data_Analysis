import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Weather Data Analysis Dashboard",
    page_icon="🌦️",
    layout="wide"
)


# Load Dataset
@st.cache_data
def load_data():
    data = pd.read_csv("weather_data.csv")
    data["Formatted Date"] = pd.to_datetime(
        data["Formatted Date"],
        format="%m/%d/%Y",
        errors="coerce"
    )
    data = data.drop_duplicates()
    return data


weather_data = load_data()


# Dashboard Title
st.title("Weather Data Analysis Dashboard")
st.write(
    "Explore temperature, humidity, weather conditions "
    "and relationships between weather variables."
)


# Dashboard Filters
st.sidebar.title("Dashboard Filters")

minimum_date = weather_data["Formatted Date"].min().date()
maximum_date = weather_data["Formatted Date"].max().date()

start_date = st.sidebar.date_input(
    "Start Date",
    value=minimum_date,
    min_value=minimum_date,
    max_value=maximum_date
)

end_date = st.sidebar.date_input(
    "End Date",
    value=maximum_date,
    min_value=minimum_date,
    max_value=maximum_date
)

weather_conditions = sorted(weather_data["Summary"].dropna().unique())

selected_conditions = st.sidebar.multiselect(
    "Weather Condition",
    weather_conditions,
    default=list(weather_conditions)
)

precipitation_types = sorted(
    weather_data["Precip Type"].dropna().unique()
)

if weather_data["Precip Type"].isna().any():
    precipitation_types.append("Missing (not assigned)")

selected_precipitation = st.sidebar.multiselect(
    "Precipitation Type",
    precipitation_types,
    default=precipitation_types
)


# Filter Dataset
filtered_data = weather_data[
    (weather_data["Formatted Date"].dt.date >= start_date) &
    (weather_data["Formatted Date"].dt.date <= end_date) &
    (weather_data["Summary"].isin(selected_conditions))
]

if "Missing (not assigned)" in selected_precipitation:
    precipitation_filter = (
        filtered_data["Precip Type"].isin(selected_precipitation) |
        filtered_data["Precip Type"].isna()
    )
else:
    precipitation_filter = filtered_data["Precip Type"].isin(
        selected_precipitation
    )

filtered_data = filtered_data[precipitation_filter]


# Weather Metrics
st.subheader("Weather at a Glance")

if filtered_data.empty:
    average_temperature = "N/A"
    highest_temperature = "N/A"
    average_humidity = "N/A"
    number_of_days = "0"
else:
    average_temperature = (
        str(round(filtered_data["Temperature (C)"].mean(), 2)) + " °C"
    )
    highest_temperature = (
        str(round(filtered_data["Temperature (C)"].max(), 2)) + " °C"
    )
    average_humidity = (
        str(round(filtered_data["Humidity"].mean() * 100, 1)) + "%"
    )
    number_of_days = str(
        filtered_data["Formatted Date"].dt.date.nunique()
    )

metric1, metric2, metric3, metric4 = st.columns(4)

metric1.metric("Average Temperature", average_temperature)
metric2.metric("Highest Temperature", highest_temperature)
metric3.metric("Average Humidity", average_humidity)
metric4.metric("Number of Days", number_of_days)


# Research Question 1
st.subheader("1. How is temperature distributed across the observations?")

if filtered_data.empty:
    st.info("No data matches the selected filters.")
else:
    chart1, chart2 = st.columns(2)

    temperature_chart = px.histogram(
        filtered_data,
        x="Temperature (C)",
        nbins=30,
        title="Temperature Distribution",
        color_discrete_sequence=["#00BFFF",
        ]
    )
    temperature_chart.update_layout(template="plotly_dark")
    chart1.plotly_chart(temperature_chart, use_container_width=True)

    with chart1.expander("Understand this chart"):
        st.write("This histogram shows how often different temperature values appear.")
        st.write("The horizontal axis shows temperature in °C. The vertical axis shows the number of observations in each temperature range.")
        st.write("A taller bar means that more observations fall within that temperature range.")
        st.write("In the current selection, the average temperature is", round(filtered_data["Temperature (C)"].mean(), 2), "°C and the median is", round(filtered_data["Temperature (C)"].median(), 2), "°C.")

    daily_temperature = (
        filtered_data.groupby("Formatted Date")["Temperature (C)"]
        .mean()
        .reset_index()
    )

    daily_chart = px.line(
        daily_temperature,
        x="Formatted Date",
        y="Temperature (C)",
        title="Daily Average Temperature",
        color_discrete_sequence=["#00BFFF"]
    )
    daily_chart.update_layout(template="plotly_dark")
    chart2.plotly_chart(daily_chart, use_container_width=True)

    with chart2.expander("Understand this chart"):
        st.write("This line chart shows how the average temperature changes from day to day.")
        st.write("The horizontal axis shows the date. The vertical axis shows the daily average temperature in °C.")
        st.write("A rising line means the daily average temperature increased. A falling line means it decreased.")
        st.write("For the current selection, the daily averages range from", round(daily_temperature["Temperature (C)"].min(), 2), "°C to", round(daily_temperature["Temperature (C)"].max(), 2), "°C.")


# Research Question 2
st.subheader("2. How does humidity vary across the observations?")

if filtered_data.empty:
    st.info("No data matches the selected filters.")
else:
    humidity_chart = px.histogram(
        filtered_data,
        x="Humidity",
        nbins=30,
        title="Humidity Distribution",
        color_discrete_sequence=["#00BFFF"]
    )
    humidity_chart.update_layout(template="plotly_dark")
    st.plotly_chart(humidity_chart, use_container_width=True)

    with st.expander("Understand this chart"):
        st.write("This histogram shows how frequently different humidity levels occur.")
        st.write("The horizontal axis shows humidity. The vertical axis shows the number of observations in each humidity range.")
        st.write("Humidity is stored between 0 and 1 in this dataset. For example, 0.80 means 80% humidity.")
        st.write("In the current selection, average humidity is", round(filtered_data["Humidity"].mean() * 100, 1), "% and the median is", round(filtered_data["Humidity"].median() * 100, 1), "%.")


# Research Question 3
st.subheader("3. Which weather conditions occur most frequently?")

if filtered_data.empty:
    st.info("No data matches the selected filters.")
else:
    weather_counts = (
        filtered_data["Summary"]
        .value_counts()
        .reset_index()
    )
    weather_counts.columns = ["Weather Condition", "Observations"]

    weather_chart = px.bar(
        weather_counts,
        x="Weather Condition",
        y="Observations",
        title="Weather Condition Frequency",
        color_discrete_sequence=["#00BFFF"]
    )
    weather_chart.update_layout(
        template="plotly_dark",
        showlegend=False
    )
    st.plotly_chart(weather_chart, use_container_width=True)

    with st.expander("Understand this chart"):
        st.write("This bar chart compares how frequently each weather condition was recorded.")
        st.write("The horizontal axis lists weather conditions. The vertical axis shows their observation counts.")
        st.write("A taller bar means that the condition appeared more often in the filtered data.")
        st.write("The most frequent condition in the current selection is", weather_counts.iloc[0]["Weather Condition"], "with", int(weather_counts.iloc[0]["Observations"]), "observations.")

    st.write(
        "Most common weather condition:",
        weather_counts.iloc[0]["Weather Condition"]
    )


# Research Question 4
st.subheader("4. Is there a relationship between temperature and humidity?")

if filtered_data.empty:
    st.info("No data matches the selected filters.")
else:
    chart1, chart2 = st.columns(2)

    temperature_humidity_chart = px.scatter(
        filtered_data,
        x="Temperature (C)",
        y="Humidity",
        title="Temperature vs Humidity",
        color_discrete_sequence=["#00BFFF"]
    )
    temperature_humidity_chart.update_layout(template="plotly_dark")
    chart1.plotly_chart(
        temperature_humidity_chart,
        use_container_width=True
    )

    with chart1.expander("Understand this chart"):
        st.write("Each dot represents one weather observation.")
        st.write("The horizontal axis shows temperature in °C. The vertical axis shows humidity.")
        st.write("A downward pattern means humidity tends to be lower when temperature is higher. An upward pattern means they tend to increase together.")
        st.write("The correlation for the current selection is", round(filtered_data["Temperature (C)"].corr(filtered_data["Humidity"]), 2), ".")

    correlation_data = filtered_data[
        ["Temperature (C)", "Humidity", "Apparent Temperature (C)"]
    ]
    correlation_chart = px.imshow(
        correlation_data.corr(),
        text_auto=True,
        title="Correlation Heatmap",
        color_continuous_scale="Blues",
        aspect="auto"
    )
    correlation_chart.update_layout(template="plotly_dark")
    chart2.plotly_chart(correlation_chart, use_container_width=True)

    with chart2.expander("Understand this chart"):
        st.write("This heatmap shows the correlation between the three weather measurements displayed.")
        st.write("Correlation values range from -1 to +1. Values closer to +1 show a positive relationship; values closer to -1 show a negative relationship; values near 0 show a weak linear relationship.")
        st.write("The diagonal values are 1 because each variable is perfectly correlated with itself.")
        st.write("Use the Temperature and Humidity cell to examine the relationship asked in Research Question 4.")

    correlation = filtered_data["Temperature (C)"].corr(
        filtered_data["Humidity"]
    )
    st.write("Temperature and humidity correlation:", round(correlation, 2))


# Research Question 5
st.subheader(
    "5. How closely does apparent temperature relate to actual temperature?"
)

if filtered_data.empty:
    st.info("No data matches the selected filters.")
else:
    apparent_chart = px.scatter(
        filtered_data,
        x="Temperature (C)",
        y="Apparent Temperature (C)",
        title="Actual Temperature vs Apparent Temperature",
        color_discrete_sequence=["#00BFFF"]
    )
    apparent_chart.update_layout(template="plotly_dark")
    st.plotly_chart(apparent_chart, use_container_width=True)

    with st.expander("Understand this chart"):
        st.write("Each dot represents one observation, comparing actual temperature with apparent temperature.")
        st.write("The horizontal axis shows actual temperature in °C. The vertical axis shows apparent temperature in °C.")
        st.write("Dots close to a straight rising line indicate that the two measurements move closely together.")
        st.write("Their correlation in the current selection is", round(filtered_data["Temperature (C)"].corr(filtered_data["Apparent Temperature (C)"]), 2), ".")

    apparent_correlation = filtered_data["Temperature (C)"].corr(
        filtered_data["Apparent Temperature (C)"]
    )
    st.write(
        "Actual and apparent temperature correlation:",
        round(apparent_correlation, 2)
    )


# Key Weather Insights
st.subheader("Key Weather Insights")

if filtered_data.empty:
    st.info("No insights are available for the selected filters.")
else:
    average_temp_value = filtered_data["Temperature (C)"].mean()
    highest_temp_value = filtered_data["Temperature (C)"].max()
    average_humidity_value = filtered_data["Humidity"].mean() * 100
    common_condition = filtered_data["Summary"].value_counts().idxmax()
    temp_humidity_corr = filtered_data["Temperature (C)"].corr(
        filtered_data["Humidity"]
    )

    st.write("Average temperature:", round(average_temp_value, 2), "°C")
    st.write("Highest temperature:", round(highest_temp_value, 2), "°C")
    st.write("Average humidity:", round(average_humidity_value, 1), "%")
    st.write("Most common weather condition:", common_condition)
    st.write("Temperature and humidity correlation:", round(temp_humidity_corr, 2))


# Raw Data
show_data = st.checkbox("Show Raw Data")

if show_data:
    st.subheader("Filtered Weather Data")
    st.dataframe(filtered_data, use_container_width=True)
