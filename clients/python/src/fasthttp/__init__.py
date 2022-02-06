__version__ = "0.1.0"

import base64
from dataclasses import asdict, dataclass, field
import json
import logging
from typing import Dict, List, Tuple, Union
import uuid

import httpcore


def create_connection_pool():
    return httpcore.ConnectionPool()


pool = create_connection_pool()
FASTHTTP_SERVER_ENDPOINT = "http://localhost:4000/api/v1/requests/"
#  FASTHTTP_SERVER_ENDPOINT = "http://localhost:4444/api/v1/requests/"
FASTHTTP_SERVER_HEADERS = {
    "content-type": "application/json",
    "accept": "application/json",
}


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
            url=self.url,
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

    serialized_requests = json.dumps(
        dict(requests=[x.asdict() for x in requests])
    ).encode()
    resp = pool.request(
        method="POST",
        url=FASTHTTP_SERVER_ENDPOINT,
        headers=FASTHTTP_SERVER_HEADERS,
        content=serialized_requests,
    )

    # TODO validate that response status is 200

    responses = json.loads(resp.content)["responses"]


def __httpbin_req(path, method="GET", headers={}, body=None):
    headers = {
        **headers,
        **{
            "content-type": "application/json",
            "accept": "application/json",
            "banana": "apple",
        },
    }
    return Request(
        url=f"https://httpbin.org{path}",
        #  url=f"http://localhost:4444{path}",
        method=method,
        headers=headers,
        body=body,
    )


if __name__ == "__main__":
    resps = send(
        [
            __httpbin_req("/headers"),
            __httpbin_req("/ip"),
            __httpbin_req("/delete", method="DELETE", body=b"name=danish&age=1"),
            __httpbin_req("/get?id=cool&name=danish"),
            __httpbin_req("/patch", method="PATCH", body=b"name=danish&age=2"),
            __httpbin_req("/post", method="POST", body=b"name=danish&age=3"),
            __httpbin_req("/put", method="PUT", body=b"name=danish&age=4"),
            __httpbin_req(
                "/status/200,300,401,402,500",
                method="DELETE",
                body=b"name=danish&age=1",
            ),
            __httpbin_req(
                "/status/200,300,401,402,500", method="GET", body=b"name=danish&age=1"
            ),
            __httpbin_req(
                "/status/200,300,401,402,500", method="PATCH", body=b"name=danish&age=2"
            ),
            __httpbin_req(
                "/status/200,300,401,402,500", method="POST", body=b"name=danish&age=3"
            ),
            __httpbin_req(
                "/status/200,300,401,402,500", method="PUT", body=b"name=danish&age=4"
            ),
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

    def print_headers(headers):
        for k, v in headers:
            print(f"{k}: {v}")

    for r in resps:
        print("========================================")
        print(r["status_code"])
        print_headers(r["headers"])
        print("")
        print(r["body"])
    print("--------------------")
