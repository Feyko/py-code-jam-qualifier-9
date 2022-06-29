import logging
import typing
from dataclasses import dataclass


@dataclass(frozen=True)
class Request:
    scope: typing.Mapping[str, typing.Any]

    receive: typing.Callable[[], typing.Awaitable[object]]
    send: typing.Callable[[object], typing.Awaitable[None]]


class RestaurantManager:
    def __init__(self):
        """Instantiate the restaurant manager.

        This is called at the start of each day before any staff get on
        duty or any orders come in. You should do any setup necessary
        to get the system working before the day starts here; we have
        already defined a staff dictionary.
        """
        self.staff = {}

    async def __call__(self, request: Request):
        """Handle a request received.

        This is called for each request received by your application.
        In here is where most of the code for your system should go.

        :param request: request object
            Request object containing information about the sent
            request to your application.
        """
        match request.scope.get("type"):
            case "staff.onduty":
                self.staff[request.scope.get("id")] = request
            case "staff.offduty":
                del self.staff[request.scope.get("id")]
            case "order":
                cook = find_valid_cook(self.staff, request.scope.get("speciality"))
                if cook is None:
                    logging.fatal(f"No valid cook found for speciality {request.scope.get('speciality')}")
                order = await request.receive()
                await cook.send(order)
                result = await cook.receive()
                await request.send(result)
            case _:
                logging.fatal(f"Unknown request type {request.scope.get('type')}")


def find_valid_cook(staff: dict, speciality: str) -> Request | None:
    for v in staff.values():
        if speciality in v.scope.get("speciality"):
            return v
    return None
