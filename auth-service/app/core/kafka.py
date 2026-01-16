import json
import asyncio
import logging
from aiokafka import AIOKafkaProducer, errors as aiokafka_errors
from app.core.config import settings

logger = logging.getLogger(__name__)

producer: AIOKafkaProducer | None = None
KAFKA_PRODUCER_LOCK = asyncio.Lock()
MAX_KAFKA_RETRIES = 3
RETRY_DELAY = 2  # seconds

async def start_kafka():
    global producer
    async with KAFKA_PRODUCER_LOCK:
        if producer is not None and producer._closed is False:
            return  # already started

        # Retry connection with exponential backoff
        max_retries = 10
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                producer = AIOKafkaProducer(
                    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS
                )
                await producer.start()
                logger.info("Kafka producer started.")
                return
            except (aiokafka_errors.KafkaConnectionError, aiokafka_errors.KafkaError) as e:
                if attempt == max_retries - 1:
                    logger.error(f"Failed to connect to Kafka after {max_retries} attempts: {e}")
                    raise
                logger.warning(f"Kafka connection attempt {attempt + 1}/{max_retries} failed: {e}. Retrying in {retry_delay}s...")
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 1.5, 10)  # Exponential backoff, max 10 seconds

async def stop_kafka():
    global producer
    async with KAFKA_PRODUCER_LOCK:
        if producer is not None and producer._closed is False:
            await producer.stop()
            logger.info("Kafka producer stopped.")

async def _ensure_producer():
    global producer
    if producer is None or producer._closed:
        logger.warning("Kafka producer not started or closed, trying to start.")
        await start_kafka()
    if producer is None or producer._closed:
        raise RuntimeError("Kafka producer not available after restart attempt.")

async def _publish_with_retry(topic: str, message: dict):
    for attempt in range(1, MAX_KAFKA_RETRIES + 1):
        try:
            await _ensure_producer()
            await producer.send_and_wait(
                topic,
                json.dumps(message).encode()
            )
            break
        except (aiokafka_errors.KafkaError, aiokafka_errors.KafkaConnectionError, RuntimeError) as e:
            logger.warning(f"Kafka send failure on attempt {attempt}/{MAX_KAFKA_RETRIES}: {e}")
            if attempt == MAX_KAFKA_RETRIES:
                logger.error(f"Failed to send Kafka message after {MAX_KAFKA_RETRIES} attempts.")
                raise
            await asyncio.sleep(RETRY_DELAY)
            await start_kafka()

async def publish_user_registered(user_id: str, email: str):
    await _publish_with_retry(
        "users.events",
        {
            "event": "UserRegistered",
            "user_id": user_id,
            "email": email
        }
    )

async def publish_email_verification(email: str, user_id: str, token: str):
    await _publish_with_retry(
        "email.verification",
        {
            "event": "EmailVerificationRequested",
            "version": 1,
            "user_id": user_id,
            "email": email,
            "token": token
        }
    )

