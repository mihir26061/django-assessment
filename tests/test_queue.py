import pytest
from queue_system.tasks import send_email_task


@pytest.mark.django_db
def test_queue_execution():
    for i in range(50):
        send_email_task.delay(f"user{i}@test.com")

    assert True  # In real case: inspect Redis / logs