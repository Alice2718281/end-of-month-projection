import pandas as pd
# import matplotlib.pyplot as plt
# from matplotlib.ticker import FuncFormatter
import plotly.express as px
import plotly.io as pio

print("Load EDA")
def eda_plot(df_total, level=None, description=None, transaction_type=None):
    
    level = level.lower() if level else None
    # transaction_type = transaction_type.upper() if transaction_type else None
    
    if level == 'national':
        df_filtered = df_total

    elif level == 'region':
        df_filtered = df_total[df_total['REGION_DESC'] == description]

    elif level == 'bu':
        df_filtered = df_total[df_total['BU_DESC'] == description]

    elif level == 'location':
        df_filtered = df_total[df_total['LOCATION_DESC'] == description]

    else: 
        df_filtered = df_total  

    if transaction_type:
        df_filtered = df_filtered[df_filtered['FIN_SOURCE_TYPE_DESC'] == transaction_type]
  
    df_filtered = df_filtered[df_filtered['FIN_SOURCE_TYPE_DESC'] == transaction_type]
    df_filtered = df_filtered.groupby(['MONTH'])['TRANSACTION_AMOUNT'].sum().reset_index()
    df_filtered['Year'] = df_filtered['MONTH'].dt.year
    df_filtered['Month'] = df_filtered['MONTH'].dt.month

    # Create interactive Plotly line plot
    fig = px.line(
        df_filtered,
        x='Month',
        y='TRANSACTION_AMOUNT',
        color='Year',
        title=f'{level.capitalize()} - {description} ({transaction_type}) Transaction Amount Over Time',
        labels={'TRANSACTION_AMOUNT': 'Total Transaction Amount', 'Month': 'Month'},
        line_shape='linear'
        )
    # Convert the plot to JSON format
    graphJSON = pio.to_json(fig)
    return graphJSON