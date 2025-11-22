from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import uuid
import logging
from kafka import KafkaProducer
import json
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

print("Starting server.py") 
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
KAFKA_TOPIC = "events"
KAFKA_ACKS = 1 
KAFKA_COMPRESSION = None  
events = []

# Initialize Kafka producer
kafka_producer = None

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def make_kafka_producer(
    bootstrap_servers: str,
    acks: int = 1,  # Change to int type
    linger_ms: int = 0,
    compression_type: Optional[str] = None
) -> KafkaProducer:
    logger.debug(f"Initializing Kafka producer with bootstrap_servers={bootstrap_servers}, acks={acks}")
    try:
        producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            acks=acks,
            linger_ms=linger_ms,
            max_block_ms=10000,
            compression_type=compression_type,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            key_serializer=lambda v: (str(v).encode("utf-8") if v is not None else None),
            
        )

        logger.info(f"Kafka producer initialized for {bootstrap_servers}")
        return producer
    except Exception as e:
        logger.error(f"Failed to initialize Kafka producer: {e}")
        raise

# Lifespan event handler for startup and shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Lifespan: Starting up")  # Debug: Confirm lifespan startup
    logger.debug("Lifespan: Initializing Kafka producer")
    # Startup: Initialize Kafka producer
    global kafka_producer
    try:
        kafka_producer = make_kafka_producer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            acks=KAFKA_ACKS,
            compression_type=KAFKA_COMPRESSION,
        )
        print(f"Kafka producer created: {kafka_producer}")
    except Exception as e:
        logger.error(f"Failed to create Kafka producer: {e}")
        print(f"Startup error: Failed to create Kafka producer: {e}")
        kafka_producer = None
    
    yield 
    
    print("Lifespan: Shutting down")
    logger.debug("Lifespan: Closing Kafka producer")
    if kafka_producer is not None:
        try:
            kafka_producer.flush(timeout=10)
            kafka_producer.close()
            logger.info("Kafka producer closed successfully")
        except Exception as e:
            logger.error(f"Failed to close Kafka producer: {e}")
            print(f"Shutdown error: Failed to close Kafka producer: {e}")

try:
    app = FastAPI(lifespan=lifespan)
    print("FastAPI app created")  # Debug: Confirm app creation
    logger.info("FastAPI application initialized")
except Exception as e:
    print(f"Failed to create FastAPI app: {e}")
    logger.error(f"Failed to create FastAPI app: {e}")
    raise

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  #Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  #Allows all headers
)

# Define the event data model based on the TypeScript structure
class EventData(BaseModel):
    eventType: str
    productId: str
    userId: str


@app.post("/api/event")
async def track_event(event: EventData, request: Request):
    print("#############INSIDE THE TRACK EVENT FUNCTION#################")
    logger.debug(f"Received POST /api/event with payload: {event}")
    logger.debug(f"Request headers: {request.headers}")
    try:
        # Create event payload with additional metadata
        event_payload = {
            "event_id": str(uuid.uuid4()),
            "event_type": event.eventType,
            "product_id": event.productId,
            "user_id": event.userId,
            "timestamp": now_iso(),
        }
        
        # Store event locally (for demonstration)
        events.append(event_payload)
        logger.debug(f"Stored event locally: {event_payload}")
        
        # Send to Kafka if producer is available
        if kafka_producer is not None:
            try:
                future = kafka_producer.send(
                    topic=KAFKA_TOPIC,
                    value=event_payload,
                    key=event_payload["event_id"]
                )
                future.get(timeout=10)  # Wait for delivery confirmation
                logger.info(f"Sent event {event_payload['event_id']} to Kafka topic {KAFKA_TOPIC}")
            except Exception as e:
                logger.error(f"Failed to send event to Kafka: {e}")
                # Continue even if Kafka send fails to ensure event is stored locally
        else:
            logger.warning("Kafka producer not initialized, skipping Kafka send")
        
        logger.info(f"Processed event: {event_payload['event_id']}")
        
        return {
            "status": "success",
            "event_id": event_payload["event_id"],
            "message": "Event tracked successfully"
        }
    
    except Exception as e:
        logger.error(f"Failed to process event: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to track event: {str(e)}")

@app.get("/api/events")
async def get_events():
    """Endpoint to retrieve all stored events (for testing purposes)"""
    logger.debug(f"Fetching all events, count: {len(events)}")
    return {"events": events}

@app.get("/health")
async def health_check():
    logger.debug("Health check requested")
    kafka_status = "connected" if kafka_producer is not None else "disconnected"
    return {
        "status": "healthy",
        "timestamp": now_iso(),
        "kafka_status": kafka_status
    }

@app.get("/debug")
async def debug_info():
    """Debug endpoint to inspect server state"""
    logger.debug("Debug info requested")
    return {
        "kafka_status": "connected" if kafka_producer is not None else "disconnected",
        "event_count": len(events),
        "kafka_config": {
            "bootstrap_servers": KAFKA_BOOTSTRAP_SERVERS,
            "topic": KAFKA_TOPIC,
            "acks": KAFKA_ACKS,
            "compression": KAFKA_COMPRESSION
        }
    }