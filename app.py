from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import redis

app = Flask(__name__)
redis_client = redis.Redis(host='redis', port=6379)

@app.route('/')
def start():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    try:
        file = request.files['csvFile']
        if file and file.filename.endswith('.csv'):
            data = pd.read_csv(file)
            counts = data.drop('id', axis=1).sum()

            plt.figure(figsize=(10, 6))
            plt.bar(counts.index, counts.values)
            plt.xlabel('Columns')
            plt.ylabel('Count')
            plt.title('Count of 1s')
            plt.xticks(rotation=45)

            img_stream = BytesIO()
            plt.savefig(img_stream, format='png')
            img_stream.seek(0)
            img_data = base64.b64encode(img_stream.read()).decode('utf-8')
            plt.close()

            # Save the visualization in Redis with a user-provided name
            visualization_name = request.form['visualization_name']
            redis_client.set(visualization_name, img_data)

            return render_template('index.html', plot_image=img_data)

        return "Invalid file format."
    except Exception as e:
        return f"Error: {e}"

@app.route('/retrieve', methods=['POST'])
def retrieve():
    try:
        visualization_name = request.form['retrieval_name']
        img_data = redis_client.get(visualization_name)
        if img_data:
            return render_template('retrieved.html', plot_image=img_data.decode('utf-8'))
        else:
            return "Visualization not found."
    except Exception as e:
        return f"Error: {e}"

if __name__ == '__main__':
    app.run(debug=True)
