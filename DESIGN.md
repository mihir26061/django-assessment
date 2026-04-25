# DESIGN.md

## Section 2 — Rate-Limited Async Job Queue Design

## Problem Statement

The platform must send transactional emails while respecting a third-party provider limit of **200 emails per minute**.

Key constraints:

- Traffic may burst to **2,000 email requests in under 10 seconds**
- Failed jobs must retry automatically
- Permanently failed jobs must be captured for later inspection
- No jobs may be lost if a worker crashes during execution
- Rate limiting must be enforced centrally across all workers

---

## Architecture Options Considered

### Option 1 — Celery + Redis (**Chosen**)

**Pros**
- Mature and battle-tested in production Django systems
- Native retry/backoff support
- Supports acknowledgment semantics for crash recovery
- Strong Redis integration
- Large ecosystem / community support

**Cons**
- Additional infrastructure dependency
- More operational complexity than lightweight alternatives

---

### Option 2 — Django Q

**Pros**
- Simpler Django-native API
- Easy setup for small projects

**Cons**
- Smaller ecosystem
- Less operational maturity at scale
- Fewer tuning/configuration options

---

### Option 3 — Custom Queue Implementation

**Pros**
- Full control over implementation
- Tailored behavior possible

**Cons**
- Reinvents broker semantics
- Must manually implement durability, retries, visibility timeout, dead lettering
- Higher long-term maintenance burden

---

## Chosen Architecture

I selected **Celery with Redis** because it provides reliable delivery semantics, retry support, and production-proven worker orchestration without requiring custom queue infrastructure.

---

## High-Level Flow

```text
Application Request
    ↓
Celery Task Enqueued in Redis Broker
    ↓
Celery Worker Pulls Task
    ↓
Redis Sliding Window Rate Limiter Check
    ↓
If Allowed → Send Email
If Blocked → Retry Later
    ↓
On Failure → Exponential Backoff Retry
    ↓
After Max Retries → Dead Letter Handling
```

---

## Rate Limiter Design

## Chosen Strategy: Sliding Window (Redis Sorted Set)

I implemented a **Redis sliding-window rate limiter**.

### Why Sliding Window Over Alternatives

#### Compared to Fixed Window

Fixed window can allow burst leakage at boundaries.

Example:

- 200 requests at 12:00:59
- 200 requests at 12:01:00

This effectively allows 400 requests in 2 seconds.

---

#### Compared to Token Bucket

Token bucket smooths bursts well but is slightly more complex to reason about for strict "N per rolling minute" enforcement.

Sliding window maps directly to the provider’s requirement:
> No more than 200 emails in any rolling 60-second period.

---

## Redis Commands Used

```text
ZREMRANGEBYSCORE
ZADD
ZCARD
EXPIRE
```

---

## Atomicity Guarantee

All rate limiter operations execute inside a Redis transaction/pipeline.

This prevents race conditions where multiple workers could simultaneously check the limit and exceed the threshold.

Without atomicity:

1. Worker A checks count = 199
2. Worker B checks count = 199
3. Both proceed
4. Limit exceeded

---

## Failure Strategy Under Redis Outage

The system **fails closed**.

Meaning:

- If Redis is unavailable, email sending stops
- No tasks bypass the limiter

### Why Fail Closed

Violating provider rate limits could:

- Trigger provider bans
- Cause dropped/blacklisted emails
- Break contractual SLA expectations

Failing closed is safer than sending unthrottled.

---

## Retry Strategy

Tasks use **exponential backoff**:

```python
countdown = 2 ** self.request.retries
```

Retry schedule example:

| Retry Attempt | Delay |
|-------------|------|
| 1 | 2s |
| 2 | 4s |
| 3 | 8s |
| 4 | 16s |

---

## Dead Letter Handling

After exceeding `max_retries`:

- Task is marked permanently failed
- Failure is logged / persisted for manual inspection
- Dead-letter queue/storage can be extended later if needed

---

## Crash Recovery / Worker SIGKILL Handling

### Relevant Celery Configuration

```python
task_acks_late = True
worker_prefetch_multiplier = 1
```

---

### What Happens If Worker Is SIGKILL'd Mid-Task

Because `acks_late=True`:

- Task is **not acknowledged before execution**
- Broker still considers task unprocessed
- Task is re-queued after worker death/disconnect
- Another worker picks it up

---

### Why `worker_prefetch_multiplier=1`

Prevents workers from reserving many tasks in advance.

Without this:

- Worker may prefetch many jobs
- Crash could delay redelivery of large batches

---

## Reliability Guarantees

This implementation guarantees:

### At-Least-Once Delivery

A task may run more than once in crash scenarios, but it will not be silently lost.

---

### No Silent Loss on Crash

Unacked tasks return to broker.

---

### Global Rate Limit Enforcement

All workers share Redis limiter state.

---

## Trade-Offs / Known Limitations

### Duplicate Execution Possible

Because of at-least-once semantics:

- A task may be re-executed after crash if side effect occurred before ack

**Mitigation:**  
Production systems should use idempotency keys when sending emails.

---

### Redis Is Single Point of Coordination

Limiter depends on Redis availability.

Mitigation in production:

- Redis replication/sentinel/cluster

---

## Testing Strategy

The queue test validates:

1. **500 jobs enqueue successfully**
2. **Rate limit never exceeds 200/minute**
3. **Intentional failure triggers retry**
4. **No job is silently dropped**

---

## Why This Design Is Production Appropriate

This architecture balances:

- Reliability
- Simplicity
- Operational realism

It avoids over-engineering while still demonstrating understanding of:

- Distributed rate limiting
- Broker acknowledgment semantics
- Crash recovery
- Retry strategy
- Failure handling

---

# End of Design
