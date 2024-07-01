import streamlit as st
import pandas as pd
import os
import glob
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import plotly.express as px
import plotly.graph_objs as go
import chardet
from data import download_files_from_gdrive
import plotly.offline as pyo

# download_files_from_gdrive()
# Function to read and concatenate all CSV files
@st.cache_data
def load_data():
    download_files_from_gdrive()

    path = 'stockSenseData/'  # Directory containing CSV files
    all_files = glob.glob(os.path.join(path, "*.csv"))
    df_list = []
    
    for filename in all_files:
        # Extract the date from the filename
        base_name = os.path.basename(filename)
        date_str = base_name.split('_')[-1].replace('.csv', '')
        date = pd.to_datetime(date_str, format='%d-%b-%Y')
        
        # Read the CSV file
        df = pd.read_csv(filename)
        df['date'] = date  # Add the date to the DataFrame
        df_list.append(df)
        
    combined_df = pd.concat(df_list, axis=0, ignore_index=True)
    combined_df = combined_df.sort_values(by='date')
    combined_df.set_index('date', inplace=True)
    return combined_df

# @st.cache_data
# def detect_encoding(file_path):
#     with open(file_path, 'rb') as f:
#         result = chardet.detect(f.read())
#         return result['encoding']
#
# @st.cache_data
# def load_data():
#     download_files_from_gdrive()
#     path = 'stockSenseData/'  # Directory containing CSV files
#     all_files = glob.glob(os.path.join(path, "*.csv"))
#     df_list = []
#     try:
#         for filename in all_files:
#             # Extract the date from the filename
#             base_name = os.path.basename(filename)
#             print(filename)
#             date_str = base_name.split('_')[-1].replace('.csv', '')
#             date = pd.to_datetime(date_str, format='%d-%b-%Y')
#
#             # Detect encoding and read the CSV file
#             encoding = detect_encoding(filename)
#             df = pd.read_csv(filename, encoding=encoding)
#             df['date'] = date  # Add the date to the DataFrame
#             df_list.append(df)
#
#         if df_list:
#             combined_df = pd.concat(df_list, axis=0, ignore_index=True)
#             combined_df = combined_df.sort_values(by='date')
#             combined_df.set_index('date', inplace=True)
#             return combined_df
#         else:
#             raise ValueError("No CSV files found locally or on Google Drive.")
#     except Exception as e:
#         print("exception")


        
        
        


# Load data


# Sidebar filters
st.sidebar.header("Filters")
if st.sidebar.button('SYNC'):
    with st.spinner('Loading data...'):
        download_files_from_gdrive()
        st.success('Data Synced successfully!')

data = load_data()
# if not data:
#     data=load_data()
st.sidebar.header("Filters")
stock = st.sidebar.selectbox("Select Stock", data['Stock Name'].unique())

# sector = st.sidebar.selectbox("Select Sector", data['Sector Name'].unique())

# Filter data based on selection
# filtered_data = data[data['Stock Name'] == stock] #& (data['Sector Name'] == sector)]
# sector=filtered_data['Sector Name'].unique()[0]
# sec_fil=data[data['Sector Name']==sector]
# vol_df=sec_fil.groupby(['date'])[['Volume (Times)']].mean()
# //////////////////////////////
filtered_data = data[data['Stock Name'] == stock] #& (data['Sector Name'] == sector)]
sector=filtered_data['Sector Name'].unique()[0]
sec_fil=data[data['Sector Name']==sector]
vol_df=sec_fil.groupby(sec_fil.index)
#//////////////////////////////
# st.write(f"belongs to{sector}")

def plot_with_markers(ax, x, y, xlabel, ylabel):
    ax.plot(x, y, marker='o', linestyle='-')
    for i, (x_val, y_val) in enumerate(zip(x, y)):
        ax.annotate(f'{y_val:.2f}', (x_val, y_val), textcoords="offset points", xytext=(0,5), ha='center')
    
    # Rotate x-axis labels for better readability
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b-%Y'))
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

def plot_with_plotly(x, y, xlabel, ylabel):
    fig = px.line(x=x, y=y, markers=True, labels={ 'x': xlabel, 'y': ylabel })
    fig.update_traces(text=y, textposition="top center")
    return fig


def plot_with_plotly(x,z,y,xlabel,ylabel):
    # fig = px.line(x=x, y=y, markers=True, labels={ 'x':):#,zlabel,xlabel, ylabel):
    # fig = px.line(x=x, y=y, markers=True, labels={ 'x': xlabel, 'y': ylabel })
    # fig.update_traces(text=y, textposition="top center")
    trace1=go.Scatter(
        x=x,
        y=y,
        mode='lines+markers',
        name=f'Stocks{ylabel}'
    )
    trace2=go.Scatter(
        x=x,
        y=z,
        mode='lines+markers',
        name=f'Sector Average{ylabel}'
    )
    data = [trace1, trace2]
    layout = go.Layout(
    title='',
    xaxis=dict(title=xlabel),
    yaxis=dict(title=ylabel)
    )
    fig = go.Figure(data=data, layout=layout)
    return fig


# Plotting
st.title(f"Dashboard for {stock}")

st.write("### Delivery over time")
# fig, ax = plt.subplots(figsize=(10, 5))
# fig=plot_with_plotly(filtered_data['date'],filtered_data['Delivery (Times)'],'Date','Volume')
# plot_with_markers(ax,filtered_data['date'], filtered_data['Delivery (Times)'],'Date','Volume')
# ax.set_xlabel('Date')
# ax.set_ylabel('Delivery')
k=vol_df[['Delivery (Times)']].mean()
fig=plot_with_plotly(k.index,filtered_data['Delivery (Times)'],k['Delivery (Times)'],'Date','Delivery')
st.plotly_chart(fig)


st.write("### Volume over time")
fig, ax = plt.subplots(figsize=(10, 5))
# plot_with_markers(ax,filtered_data['date'], filtered_data['Volume (Times)'],'Date','Volume')
# fig=plot_with_plotly(filtered_data['date'], filtered_data['Volume (Times)'],'Date','Volume')
# ax.set_xlabel('Date')
# ax.set_ylabel('Volume')
k=vol_df[['Volume (Times)']].mean()
fig=plot_with_plotly(k.index, filtered_data['Volume (Times)'],k['Volume (Times)'],'Date','Volume')
st.plotly_chart(fig)

st.write("### Change % over time")
fig, ax = plt.subplots(figsize=(10, 5))
# plot_with_markers(ax,filtered_data['date'], filtered_data['Chg %'],'Date','Change %')
# fig=plot_with_plotly(filtered_data['date'], filtered_data['Chg %'],'Date','Change %')
# ax.set_xlabel('Date')
# ax.set_ylabel('Change %')
k=vol_df[['Chg %']].mean()
fig=plot_with_plotly(k.index, filtered_data['Chg %'],k['Chg %'],'Date','Change %')                    
st.plotly_chart(fig)

st.write("### OI Change over time")
fig, ax = plt.subplots(figsize=(10, 5))
# plot_with_markers(ax,filtered_data['date'], filtered_data['OI Chg %'],'Date','OI Change')
# fig=plot_with_plotly(filtered_data['date'], filtered_data['OI Chg %'],'Date','OI Change')
# ax.set_xlabel('Date')
# ax.set_ylabel('OI Change')
k=vol_df[['OI Chg %']].mean()
fig=plot_with_plotly(k.index, filtered_data['OI Chg %'],k['OI Chg %'],'Date','OI Change')                   
st.plotly_chart(fig)

# st.write("### NSE Data over time")
# fig, ax = plt.subplots()
# ax.plot(filtered_data['date'], filtered_data['NSE Data'])
# ax.set_xlabel('Date')
# ax.set_ylabel('NSE Data')
# st.pyplot(fig)

st.write("### Rollover over time")
fig, ax = plt.subplots(figsize=(10, 5))
# plot_with_markers(ax,filtered_data['date'], filtered_data['Rollover'],'Date','Rollover')
# fig=plot_with_plotly(filtered_data['date'], filtered_data['Rollover'],'Date','Rollover')
# ax.set_xlabel('Date')
# ax.set_ylabel('Rollover')
k=vol_df[['Rollover']].mean()
fig=plot_with_plotly(k.index, filtered_data['Rollover'],k['Rollover'],'Date','Rollover')                     
st.plotly_chart(fig)
