from services.base import CRUDService
from models.models import Patient


class PatientService(CRUDService):
    model = Patient
