
from kafka import KafkaConsumer
import json
import logging
import requests # Added for HTTP requests
from pprint import pprint

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "events"
 # Changed name to separate from other tests

# PASTE YOUR LAMBDA URL HERE
LAMBDA_URL = "https://zbvrfxgjhl.execute-api.ap-south-1.amazonaws.com/default/lamda-kafka-local"
# ---------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_consumer():
    consumer = KafkaConsumer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda v: json.loads(v.decode('utf-8')),
        key_deserializer=lambda k: k.decode('utf-8') if k else None,
    )
    consumer.subscribe(['events'])
    return consumer

def push_to_lambda(message_data):
    """Sends the Kafka message data to AWS Lambda via HTTP POST"""
    try:
        # Wrap the kafka data into a payload for Lambda
        payload = {
            "source": "kafka-bridge",
            "topic": message_data.topic,
            "partition": message_data.partition,
            "offset": message_data.offset,
            "data": message_data.value # The actual event content
        }

        print(f"📤 Sending Offset {message_data.offset} to Lambda...")
        
        response = requests.post(LAMBDA_URL, json=payload)
        
        if response.status_code == 200:
            print(f"SUCCESS: Lambda processed message! (Status: {response.status_code})")
            # Optional: Print Lambda's response body
            # print(response.json())
        else:
            print(f" WARNING: Lambda returned error {response.status_code}")
            print(response.text)

    except Exception as e:
        print(f"NETWORK ERROR: Could not reach Lambda. {e}")

def main():
    logger.info("Starting Kafka-to-Lambda Bridge...")
    
    try:
        consumer = create_consumer()
        print(f" Connected to Kafka at {KAFKA_BOOTSTRAP_SERVERS}")
        print(f" Forwarding to Lambda: {LAMBDA_URL}")
        print("\nWaiting for messages... (Press Ctrl+C to stop)\n")
        
        for message in consumer:
            print("-" * 50)
            print("NEW EVENT RECEIVED ")
            pprint(message.value, indent=2)
            
            # Push to Lambda immediately
            push_to_lambda(message)
            
    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception as e:
        logger.error(f"Bridge crashed: {e}")
    finally:
        if 'consumer' in locals():
            consumer.close()
            logger.info("Consumer closed.")

if __name__ == "__main__":
    main()