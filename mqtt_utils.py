from awsiot import mqtt_connection_builder
import awscrt
import logging
import cv2

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def connect_to_aws_iot(endpoint, client_id, cert_filepath, pri_key_filepath, ca_filepath):
    logging.info("Connecting to AWS IoT")
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=endpoint,
        client_id=client_id,
        cert_filepath=cert_filepath,
        pri_key_filepath=pri_key_filepath,
        ca_filepath=ca_filepath,
        keep_alive_secs=30)
    mqtt_connection.connect()
    logging.info("Connected to AWS IoT")
    return mqtt_connection

def publish_image(mqtt_connection, topic_name, frame):
    image_bytes = cv2.imencode('.jpg', frame)[1].tobytes()
    mqtt_connection.publish(topic=topic_name, payload=image_bytes, qos=awscrt.mqtt.QoS.AT_LEAST_ONCE)
    logging.info("Image published to MQTT topic: {}".format(topic_name))
