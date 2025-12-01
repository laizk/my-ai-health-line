from services.base import CRUDService
from models.models import UserAccount


class UserService(CRUDService):
    model = UserAccount
