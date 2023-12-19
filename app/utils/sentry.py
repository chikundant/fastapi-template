import sentry_sdk

from app.core.settings import Settings


def init_sentry(settings: Settings):
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )