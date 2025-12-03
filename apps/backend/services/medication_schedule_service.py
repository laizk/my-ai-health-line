from services.base import CRUDService
from models.models import MedicationSchedule


class MedicationScheduleService(CRUDService):
    model = MedicationSchedule
