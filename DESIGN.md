# Job Queue Design

## Choice: Celery + Redis

### Why:
- Proven reliability
- Built-in retries
- Strong ecosystem

## Rate Limiter: Token Bucket

### Why:
- Simple
- Efficient
- Works well with bursts

## Atomicity:
- Redis DECR is atomic

## Failure Handling:
- task_acks_late=True ensures requeue
- worker_prefetch_multiplier=1 avoids batching

## Redis Failure:
- System fails CLOSED (safe)