import json
from aiokafka import AIOKafkaProducer
from app.core.config import settings

producer: AIOKafkaProducer | None = None

async def start_kafka():
    global producer
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS
    )
    await producer.start()

async def stop_kafka():
    await producer.stop()

async def publish_user_registered(user_id: str, email: str):
    await producer.send_and_wait(
        "users.events",
        json.dumps({
            "event": "UserRegistered",
            "user_id": user_id,
            "email": email
        }).encode()
    )

async def publish_email_verification(email: str, user_id: str, token: str):
    if not producer:
        raise RuntimeError("Kafka not started")

    await producer.send_and_wait(
        "email.verification",
        json.dumps({
            "event": "EmailVerificationRequested",
            "version": 1,
            "user_id": user_id,
            "email": email,
            "token": token
        }).encode()
    )


