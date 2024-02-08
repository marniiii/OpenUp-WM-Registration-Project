from .celery import app as celery_app

__all__ = ("celery_app",)

#if this isn't working add to the account init also and personal