import gradio as gr
import paho.mqtt.client as mqtt
import json
import time
import threading
import plotly.graph_objs as go

# Global variables
data_points = []
MAX_DATA_POINTS = 100

# MQTT setup
MQTT_BROKER = "broker.hivemq.com"
MQTT_TOPIC = "test_fan"

# Callback when a message is received from the server
def on_message(client, userdata, message):
    global data_points
    try:
        payload = message.payload.decode()
        value = float(payload)  # Assume the payload is a single float value
        data_points.append({"timestamp": time.time(), "value": value})
        
        # Keep only the last MAX_DATA_POINTS
        if len(data_points) > MAX_DATA_POINTS:
            data_points = data_points[-MAX_DATA_POINTS:]
    except ValueError:
        print(f"Received invalid payload: {payload}")

# Set up MQTT client
client = mqtt.Client(client_id="gradio_client", protocol=mqtt.MQTTv311)
client.on_message = on_message
client.connect(MQTT_BROKER, 1883, 60)
client.subscribe(MQTT_TOPIC)

# Start MQTT loop in a separate thread
mqtt_thread = threading.Thread(target=client.loop_forever)
mqtt_thread.start()

# Gradio components
def update_chart():
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=[point["timestamp"] for point in data_points],
        y=[point["value"] for point in data_points],
        mode='lines+markers'
    ))
    fig.update_layout(
        title="MQTT Data Visualization",
        xaxis_title="Timestamp",
        yaxis_title="Value"
    )
    return fig

with gr.Blocks() as app:
    gr.Markdown("# MQTT Data Visualization")
    plot = gr.Plot()
    
    gr.Markdown(f"Listening to MQTT topic: {MQTT_TOPIC}")
    
    # Update the chart every second
    app.load(update_chart, None, plot, every=1)

# Launch the app
app.launch()