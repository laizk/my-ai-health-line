from services.base import CRUDService
from models.models import UserPatientAccess


class UserPatientAccessService(CRUDService):
    model = UserPatientAccess
