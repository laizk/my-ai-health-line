from services.base import CRUDService
from models.models import Notification


class NotificationService(CRUDService):
    model = Notification
