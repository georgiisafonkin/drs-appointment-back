import json
from aiokafka import AIOKafkaConsumer
from app.core.config import settings
from app.consumers.email_verification import handle_email_verification

consumer: AIOKafkaConsumer | None = None

async def start_consumer():
    global consumer
    consumer = AIOKafkaConsumer(
        "email.verification",
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id="notification-service",
        enable_auto_commit=False
    )
    await consumer.start()

    async for msg in consumer:
        event = json.loads(msg.value)
        await handle_email_verification(event)
        await consumer.commit()

async def stop_consumer():
    if consumer:
        await consumer.stop()
