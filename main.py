import streamlit as st
import pandas as pd
import os
import glob
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import plotly.express as px
import plotly.graph_objs as go

# Function to read and concatenate all CSV files within a date range
@st.cache_data
def load_data(start_date=None, end_date=None):
    path = 'stockSenseData/'  # Directory containing CSV files
    all_files = glob.glob(os.path.join(path, "*.csv"))
    df_list = []
    
    for filename in all_files:
        # Extract the date from the filename
        base_name = os.path.basename(filename)
        date_str = base_name.split('_')[-1].replace('.csv', '')
        date = pd.to_datetime(date_str, format='%d-%b-%Y')
        
        # Filter files by date range if provided
        if (start_date is not None and date < start_date) or (end_date is not None and date > end_date):
            continue
        
        # Read the CSV file
        df = pd.read_csv(filename)
        df['date'] = date  # Add the date to the DataFrame
        df_list.append(df)
        
    combined_df = pd.concat(df_list, axis=0, ignore_index=True)
    combined_df = combined_df.sort_values(by='date')
    combined_df.set_index('date', inplace=True)
    return combined_df

# Streamlit interface for date range selection
st.sidebar.header("Date Range Selection")
start_date = st.sidebar.date_input("Start Date", value=None)
end_date = st.sidebar.date_input("End Date", value=None)

# Convert dates to pandas datetime format
start_date = pd.to_datetime(start_date) if start_date else None
end_date = pd.to_datetime(end_date) if end_date else None

# Load data
data = load_data(start_date, end_date)

# Sidebar filters
st.sidebar.header("Filters")
stock = st.sidebar.selectbox("Select Stock", data['Stock Name'].unique())

# Filter data based on selection
filtered_data = data[data['Stock Name'] == stock]
sector = filtered_data['Sector Name'].unique()[0]
sec_fil = data[data['Sector Name'] == sector]
vol_df = sec_fil.groupby(sec_fil.index)

def plot_with_plotly(x, y, z, xlabel, ylabel):
    trace1 = go.Scatter(
        x=x,
        y=y,
        mode='lines+markers',
        name=f'Stocks {ylabel}'
    )
    trace2 = go.Scatter(
        x=x,
        y=z,
        mode='lines+markers',
        name=f'Sector Average {ylabel}',
        line=dict(color='red')  # Set the color of the average line to red
    )
    data = [trace1, trace2]
    layout = go.Layout(
        title='',
        xaxis=dict(
            title=xlabel,
            titlefont=dict(
                size=16,
                color='black',
                family='Arial, sans-serif, bold'  # Make x-axis label bold
            ),
            tickfont=dict(
                size=14,
                color='black',
                family='Arial, sans-serif, bold'  # Make x-axis values bold
            )
        ),
        yaxis=dict(
            title=ylabel,
            titlefont=dict(
                size=16,
                color='black',
                family='Arial, sans-serif, bold'  # Make y-axis label bold
            ),
            tickfont=dict(
                size=14,
                color='black',
                family='Arial, sans-serif, bold'  # Make y-axis values bold
            )
        )
    )
    fig = go.Figure(data=data, layout=layout)
    return fig




# Plotting
st.title(f"Dashboard for {stock}")

st.write("### Delivery over time")
k = vol_df[['Delivery (Times)']].mean()
fig = plot_with_plotly(k.index, filtered_data['Delivery (Times)'], k['Delivery (Times)'], 'Date', 'Delivery')
st.plotly_chart(fig)

st.write("### Volume over time")
k = vol_df[['Volume (Times)']].mean()
fig = plot_with_plotly(k.index, filtered_data['Volume (Times)'], k['Volume (Times)'], 'Date', 'Volume')
st.plotly_chart(fig)

st.write("### Change % over time")
k = vol_df[['Chg %']].mean()
fig = plot_with_plotly(k.index, filtered_data['Chg %'], k['Chg %'], 'Date', 'Change %')
st.plotly_chart(fig)

st.write("### OI Change over time")
k = vol_df[['OI Chg %']].mean()
fig = plot_with_plotly(k.index, filtered_data['OI Chg %'], k['OI Chg %'], 'Date', 'OI Change')
st.plotly_chart(fig)

st.write("### Rollover over time")
k = vol_df[['Rollover']].mean()
fig = plot_with_plotly(k.index, filtered_data['Rollover'], k['Rollover'], 'Date', 'Rollover')
st.plotly_chart(fig)
