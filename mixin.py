from typing import Protocol, Self
#from type_intersections import Intersection
from typing_protocol_intersection import ProtocolIntersection

class User:
    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def name(self) -> str:
        return "ExampleUser"


class Request:
    user: User


class ViewProtocol(Protocol):
    def dispatch(self, request: Request) -> str:
        ...

class MixinProtocol(Protocol):
    def valid_user(self, user: str) -> bool:
        ...

class View:
    def dispatch(self, request: Request) -> str:
        return "FOO"


class LoginRequiredMixin:
    def valid_user(self, user: str) -> bool:
        return user.startswith("Example")

    def dispatch(self: View & "LoginRequiredMixin", request: Request):
        if not request.user.is_authenticated or not self.valid_user(request.user.name):
            raise RuntimeError("Not allowed")
        return super().dispatch(request)
