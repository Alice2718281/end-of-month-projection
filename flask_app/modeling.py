import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import calendar

# df_total = pd.read_csv(r'C:\Users\Qihang Tang\OneDrive\桌面\APAN\Capstone\flask_app\df_total.csv')
# df_total['MONTH'] = pd.to_datetime(df_total['MONTH'])
# df_total['YEAR'] = pd.to_datetime(df_total['YEAR'])
# df_total['GL_TRANSACTION_EFFECTIVE_DT'] = pd.to_datetime(df_total['GL_TRANSACTION_EFFECTIVE_DT'])

print("Load Prediction Model")
def generate_prediction_all_type(df_total, month, year, level='national', region=None, BU=None, location=None, days_to_predict=10, transaction_type=None):

    print(f"Parameters - Month: {month}, Year: {year}, Level: {level}, Region: {region}, BU: '{BU}', Location: {location}")

    metrics_list = []
    predictions_list = []

    df_filtered = df_total[(df_total['GL_TRANSACTION_EFFECTIVE_DT'].dt.month == month) & 
                           (df_total['GL_TRANSACTION_EFFECTIVE_DT'].dt.year == year)]

    if transaction_type:
        transaction_type = transaction_type.strip().upper()
        df_filtered = df_filtered[df_filtered['FIN_SOURCE_TYPE_DESC'] == transaction_type]

    level = level.lower() if level else None

    if level == 'national':
        df_filtered = df_filtered.groupby('GL_TRANSACTION_EFFECTIVE_DT')['TRANSACTION_AMOUNT'].sum().reset_index()
    elif level == 'region' and region is not None:
        df_filtered['REGION_DESC'] = df_filtered['REGION_DESC'].str.strip().str.upper()
        region = region.strip().upper()
        df_filtered = df_filtered[df_filtered['REGION_DESC'] == region]
        df_filtered = df_filtered.groupby(['GL_TRANSACTION_EFFECTIVE_DT', 'REGION_DESC'])['TRANSACTION_AMOUNT'].sum().reset_index()
    elif level == 'bu' and BU is not None:
        df_filtered['BU_DESC'] = df_filtered['BU_DESC'].str.strip().str.upper()
        BU = BU.strip().upper()
        df_filtered = df_filtered[df_filtered['BU_DESC'] == BU]
        df_filtered = df_filtered.groupby(['GL_TRANSACTION_EFFECTIVE_DT', 'BU_DESC'])['TRANSACTION_AMOUNT'].sum().reset_index()
    elif level == 'location' and location is not None:
        df_filtered['LOCATION_DESC'] = df_filtered['LOCATION_DESC'].str.strip().str.upper()
        location = location.strip().upper()
        df_filtered = df_filtered[df_filtered['LOCATION_DESC'] == location]
        df_filtered = df_filtered.groupby(['GL_TRANSACTION_EFFECTIVE_DT', 'LOCATION_DESC'])['TRANSACTION_AMOUNT'].sum().reset_index()

    df_filtered['cumulative_daily_cost'] = df_filtered['TRANSACTION_AMOUNT'].cumsum()

    if df_filtered.empty:
        return None, None, None  # Return if there is no data for the specified filters

    df_filtered['date_ordinal'] = df_filtered['GL_TRANSACTION_EFFECTIVE_DT'].map(lambda x: x.toordinal())
    monthly_cost_actual = df_filtered['TRANSACTION_AMOUNT'].sum()
    monthly_cost = np.array([monthly_cost_actual])
    num_days_in_month = calendar.monthrange(year, month)[1]
    actual_days_to_predict = min(days_to_predict, num_days_in_month) - 1
    X = df_filtered[['date_ordinal']].iloc[:actual_days_to_predict]
    y = df_filtered['cumulative_daily_cost'].iloc[:actual_days_to_predict]
    x_test = pd.DataFrame({'date_ordinal': [df_filtered['date_ordinal'].iloc[-1]]})

    if len(X) < 2:  # Ensure sufficient data points for regression
        return None, None, None

    linear_model = LinearRegression()
    linear_model.fit(X, y)
    y_pred = linear_model.predict(x_test)
    y_pred_train = linear_model.predict(X)

    mse_train = mean_squared_error(y, y_pred_train)
    rmse_train = np.sqrt(mse_train)
    mae_train = mean_absolute_error(y, y_pred_train)
    r2_train = r2_score(y, y_pred_train)
    mape_train = np.mean(np.abs((y - y_pred_train) / y)) * 100

    mse_test = mean_squared_error(monthly_cost, y_pred)
    rmse_test = np.sqrt(mse_test)
    mae_test = mean_absolute_error(monthly_cost, y_pred)
    mape_test = np.mean(np.abs((monthly_cost - y_pred) / monthly_cost)) * 100

    metrics_list.append({
        'month': month, 'year': year,
        'rmse_train': rmse_train, 'mae_train': mae_train, 'r2_train': r2_train, 'mape_train': mape_train,
        'rmse_test': rmse_test, 'mae_test': mae_test, 'mape_test': mape_test
    })
    predictions_list.append({
        'month': month, 'year': year, 'y_actual_start': y_pred_train[0],
        'y_actual': monthly_cost_actual, 'y_pred': y_pred[0]
    })

    return df_filtered, metrics_list, predictions_list

# # Test function (for debugging purposes)
# if __name__ == "__main__":
#     level = "bu"  # Example input for testing
#     BU = "OPS - MID SOUTH BU "  # Example input for testing
#     transaction_type = "repair orders"  # Example input for testing
#     df_filtered, metrics_list, predictions_list = generate_prediction_all_type(df_total, month=1, year=2024, level='bu', BU='OPS - MID SOUTH BU  ', days_to_predict=12, transaction_type='repair orders')
#     print(predictions_list)