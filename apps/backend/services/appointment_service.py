from services.base import CRUDService
from models.models import Appointment


class AppointmentService(CRUDService):
    model = Appointment
