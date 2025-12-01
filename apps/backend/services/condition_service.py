from services.base import CRUDService
from models.models import Condition


class ConditionService(CRUDService):
    model = Condition
