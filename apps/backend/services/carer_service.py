from services.base import CRUDService
from models.models import Carer


class CarerService(CRUDService):
    model = Carer
