__version__ = "0.1.0"

from dataclasses import dataclass, field, asdict
from typing import List, Union, Tuple, Dict
import httpcore
import logging
import json
import uuid
import base64


def create_connection_pool():
    return httpcore.ConnectionPool()


pool = create_connection_pool()
FASTHTTP_SERVER_ENDPOINT = "http://localhost:4444/api/v1/requests/"
FASTHTTP_SERVER_HEADERS = []


Headers = Dict[str, str]
Body = Union[str, bytes, None]


@dataclass
class Request:
    # e.g. https://www.instacart.com/
    url: str
    # e.g. GET, POST, PUT, DELETE, QUERY
    method: str = "GET"
    # e.g. [("content-type", "application/json"), ("accept", "text/html")]
    headers: Headers = field(default_factory=list)
    # e.g. b"name=danish&age=5"
    # e.g. b'{"name": "danish", "age": 5}'
    body: Body = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)

    # TODO: validate request data
    def asdict(self):
        return dict(
            body=self.wrap_body(self.body),
            id=str(self.id),
            headers=self.headers,
            method=self.method,
        )

    def wrap_body(self, body):
        if body is None:
            return dict(type="empty")
        if isinstance(body, str):
            return dict(type="string", data=body)
        if isinstance(body, bytes):
            return dict(type="base64", data=base64.standard_b64encode(body).decode())
        raise ValueError(f"Unsupported body type: {type(body)}")


# Usage:
# (get_user_response, create_order_response) = FastHTTP.send((
#   Request(url="https://insta.com/v1/get_user", method="GET", ...),
#   Request(url="https://insta.com/v1/create_order", method="POST", ...),
# ))
def send(requests: List[Request]):
    # TODO: add idempotentcy
    logging.info(msg="sending_requests", requests=requests)
    # TODO: add identitying tags and DD trace info to stitch things

    serialized_requests = json.dumps([x.asdict() for x in requests]).encode()
    pool.request(
        method="POST",
        url=FASTHTTP_SERVER_ENDPOINT,
        headers=FASTHTTP_SERVER_HEADERS,
        content=serialized_requests,
    )


if __name__ == "__main__":
    logging.info(
        send(
            [
                Request(url="https://insta.com/v1/get_user", method="GET"),
                Request(url="https://insta.com/v1/create_order", method="POST"),
                Request(
                    url="https://insta.com/v1/create_order", method="POST", body=b"DOIT"
                ),
                Request(
                    url="https://insta.com/v1/create_order",
                    method="POST",
                    body="what=something+cool",
                ),
            ]
        )
    )
