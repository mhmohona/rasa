import asyncio
import warnings
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import UnknownTimeZoneError, utc

__scheduler = None

logger = logging.getLogger(__name__)


async def scheduler() -> AsyncIOScheduler:
    """Thread global scheduler to handle all recurring tasks.

    If no scheduler exists yet, this will instantiate one."""

    global __scheduler

    if not __scheduler:
        try:
            __scheduler = AsyncIOScheduler(event_loop=asyncio.get_event_loop())
            __scheduler.start()
            return __scheduler
        except UnknownTimeZoneError:
            warnings.warn(
                "apscheduler could not find a timezone and is "
                "defaulting to utc. This is probably because "
                "your system timezone is not set. "
                'Set it with e.g. echo "Europe/Berlin" > '
                "/etc/timezone"
            )
            __scheduler = AsyncIOScheduler(
                event_loop=asyncio.get_event_loop(), timezone=utc
            )
            __scheduler.start()
            return __scheduler
    elif __scheduler._eventloop == asyncio.get_event_loop():
        return __scheduler
    else:
        raise RuntimeError(
            "Detected inconsistent loop usage. "
            "Trying to schedule a task on a new event "
            "loop, but scheduler was created with a "
            "different event loop. Make sure there "
            "is only one event loop in use and that the "
            "scheduler is running on that one."
        )


def kill_scheduler() -> None:
    """Terminate the scheduler if started.

    Another call to `scheduler` will create a new scheduler."""

    global __scheduler

    if __scheduler:
        __scheduler.shutdown()
        __scheduler = None
