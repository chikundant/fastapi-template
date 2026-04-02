import sentry_sdk

from app.core.settings import Settings
from sentry_sdk.utils import BadDsn
from logging import getLogger   

logger = getLogger(__name__)


def init_sentry(settings: Settings):
    try:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
        )
    except BadDsn:
        logger.warning("Invalid Sentry DSN")