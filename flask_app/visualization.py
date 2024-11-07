import pandas as pd
import plotly.graph_objs as go

print('Loading Prediction Plot ...')
def generate_prediction_plot(df_filtered, days_to_predict, y_pred):

    df_filtered['GL_TRANSACTION_EFFECTIVE_DT'] = pd.to_datetime(df_filtered['GL_TRANSACTION_EFFECTIVE_DT'])

    # Create traces
    trace_actual = go.Scatter(
        x=df_filtered['GL_TRANSACTION_EFFECTIVE_DT'][:],
        y=df_filtered['cumulative_daily_cost'][:],
        mode='lines+markers',
        name='Actual Cumulative Cost',
        line=dict(color='blue')
    )

    trace_first_N_days = go.Scatter(
        x=df_filtered['GL_TRANSACTION_EFFECTIVE_DT'][:days_to_predict],
        y=df_filtered['cumulative_daily_cost'][:days_to_predict],
        mode='lines',
        name=f'First {days_to_predict} Days',
        line=dict(color='orange')
    )

    trace_predicted = go.Scatter(
        x=[df_filtered['GL_TRANSACTION_EFFECTIVE_DT'].iloc[-1]],
        y=[y_pred],
        mode='markers',
        name='Predicted Cost',
        marker=dict(color='red', size=10)
    )

    trace_actual_last = go.Scatter(
        x=[df_filtered['GL_TRANSACTION_EFFECTIVE_DT'].iloc[-1]],
        y=[df_filtered['cumulative_daily_cost'].iloc[-1]],
        mode='markers',
        name='Actual Cost',
        marker=dict(color='blue', size=10)
    )

    # Define the layout
    layout = go.Layout(
        title='Repair Orders Cumulative Daily Cost Over Time for 2024-01',
        xaxis=dict(title='Date'),
        yaxis=dict(
            title='Cumulative Cost',
            tickformat='$,.0f'  # Format as millions
        ),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=40, b=40)
    )

    # Create figure
    fig = go.Figure(data=[trace_actual, trace_first_N_days, trace_predicted, trace_actual_last], layout=layout)
    return fig