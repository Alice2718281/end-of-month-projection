from flask import Flask, render_template, request, jsonify, url_for
from eda import eda_plot
from modeling import generate_prediction_all_type
import pandas as pd
from visualization import generate_prediction_plot
import plotly.io as pio
from method1 import perform_analysis

app = Flask(__name__)

print("Loading df_total.csv...")
df_total = pd.read_csv(r'C:\Users\Qihang Tang\OneDrive\桌面\APAN\Capstone\flask_app\df_total.csv')
df_total['MONTH'] = pd.to_datetime(df_total['MONTH'])
df_total['YEAR'] = pd.to_datetime(df_total['YEAR'])
df_total['GL_TRANSACTION_EFFECTIVE_DT'] = pd.to_datetime(df_total['GL_TRANSACTION_EFFECTIVE_DT'])

@app.route("/")
def home():
    return render_template("5900_index_2.html")

@app.route("/get_eda_plot", methods=["POST"])
def get_eda_plot():
    # Retrieve parameters from the request
    level = request.json.get("level")
    description = request.json.get("description")
    transaction_type = request.json.get("transaction_type")
    # Generate the Plotly graph JSON
    graphJSON = eda_plot(df_total, level=level, description=description, transaction_type=transaction_type)
    return jsonify(graphJSON)

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json
    method = data.get("method")

    # Handle Method 1
    if method == 'method1': #and model == 'Neural Network':
        # Generate images for method1
        image_path_1, image_path_2, image_path_3, image_path_4, image_path_nn = perform_analysis()

        if all([image_path_1, image_path_2, image_path_3, image_path_4, image_path_nn]):
            return jsonify({
                'image_url_1': url_for('static', filename=image_path_1.split('static/')[-1]),
                'image_url_2': url_for('static', filename=image_path_2.split('static/')[-1]),
                'image_url_3': url_for('static', filename=image_path_3.split('static/')[-1]),
                'image_url_4': url_for('static', filename=image_path_4.split('static/')[-1]),
                'image_url_nn': url_for('static', filename=image_path_nn.split('static/')[-1])
            })
        else:
            return jsonify({'error': 'Failed to generate prediction images.'}), 500

    elif method == "method2":# and model == 'Linear Regression':

        days_to_predict = int(data.get("days_to_predict", 10))
        # model = data.get('model')
        month = int(data.get("month").lstrip("0")) if data.get("month") else None
        year = int(data.get("year")) if data.get("year") else None
        level = data.get("level")
        region = data.get("region")
        BU = data.get("BU")
        location = data.get("location")
        transaction_type = data.get("transaction_type")

        # Call the generate_prediction_all_type function for method 2
        df_filtered, metrics_list, predictions_list = generate_prediction_all_type(
            df_total, month, year, level=level, region=region, BU=BU,
            location=location, days_to_predict=days_to_predict, transaction_type=transaction_type
        )

        if not metrics_list or not predictions_list:
            return jsonify({'error': 'No data found for the specified filters'}), 404

        # Extract actual cost, predicted cost, and MAPE from the first entry in the predictions list
        actual_cost = predictions_list[0]['y_actual']
        predicted_cost = predictions_list[0]['y_pred']
        mape = metrics_list[0]['mape_test']

        fig = generate_prediction_plot(df_filtered, days_to_predict, predicted_cost)
        fig_json = pio.to_json(fig)

        return jsonify({
            'actual_cost': actual_cost,
            'predicted_cost': predicted_cost,
            'error_percentage': mape,
            'plot': fig_json
        })
    else:
        return jsonify({'error': 'Unsupported method selected'}), 400

if __name__ == '__main__':
    app.run(port=5500, debug=True)