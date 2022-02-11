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
    # e.g. {"content-type": "application/json", "accept": "text/html"}
    headers: Headers = field(default_factory=dict)
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

    def __repr__(self) -> str:
        headers = "\n".join(f"{k}: {v}" for k, v in self.headers.items())
        body_string = ""
        if isinstance(self.body, str):
            body_string = self.body
        elif isinstance(self.body, bytes):
            body_string = self.body.decode()

        return "\n".join(
            [f"{self.method} {self.url} HTTP/1.1or2", headers, body_string]
        )


@dataclass(frozen=True)
class Response:
    status_code: int
    request: Request
    headers: Headers
    body: Body
    meta: dict
    id: uuid.UUID = field(
        default_factory=uuid.uuid4
    )  # TODO this should be from the server

    def __repr__(self) -> str:
        headers_str = "\n".join(f"{k}: {v}" for k, v in self.headers)
        meta_str = "\n".join(f"{k}: {v}" for k, v in self.meta.items())
        return "\n".join(
            ["HTTP/1.1or2 {self.status_code}", headers_str, "", meta_str, "", self.body]
        )


@dataclass(frozen=True)
class TransportError:
    request: Request
    error_message: str
    error_code: str

    def __repr__(self) -> str:
        return "\n".join(
            [
                "Error:",
                f"error_code: {self.error_code}",
                f"error_message: {self.error_message}",
            ]
        )


def parse_response(response_json, request):
    if response_json["type"] == "response":
        return Response(
            status_code=response_json["status_code"],
            request=request,
            meta=response_json["meta"],
            headers=response_json["headers"],
            body=response_json["body"],
        )
    elif response_json["type"] == "error":
        return TransportError(
            request=request,
            error_message=response_json["error_message"],
            error_code=response_json["error_code"],
        )
    else:
        raise ValueError(f"Unsupported response type: {response_json['type']}")


# Usage:
# (get_user_response, create_order_response) = FastHTTP.send((
#   Request(url="https://insta.com/v1/get_user", method="GET", ...),
#   Request(url="https://insta.com/v1/create_order", method="POST", ...),
# ))
def send(requests: List[Request]):
    # TODO: add idempotentcy
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

    requests_dict = {str(x.id): x for x in requests}
    responses = [
        parse_response(r, requests_dict[r["id"]])
        for r in json.loads(resp.content)["responses"]
    ]
    return responses


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
    reqs = [
        __httpbin_req("/headers"),
        __httpbin_req("/ip"),
        __httpbin_req("/get?id=cool&name=danish"),
        __httpbin_req("/delete", method="DELETE", body=b"name=danish&age=1"),
        __httpbin_req("/patch", method="PATCH", body=b"name=danish&age=2"),
        __httpbin_req("/post", method="POST", body=b"name=danish&age=3"),
        __httpbin_req("/put", method="PUT", body=b"name=danish&age=4"),
        __httpbin_req("/status/200,300,401,402,500", method="GET"),
        __httpbin_req(
            "/status/200,300,401,402,500",
            method="DELETE",
            body=b"name=danish&age=1",
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
        __httpbin_req(
            "/status/200,300,401,402,500",
            method="DELETE",
            body="name=danish&age=1",
        ),
        __httpbin_req(
            "/status/200,300,401,402,500", method="PATCH", body="name=danish&age=2"
        ),
        __httpbin_req(
            "/status/200,300,401,402,500", method="POST", body="name=danish&age=3"
        ),
        __httpbin_req(
            "/status/200,300,401,402,500", method="PUT", body="name=danish&age=4"
        ),
        Request(url=f"https://dangnabbitfoobarbaz.com"),
    ]
    reqs = reqs * 5
    print("****************************************")
    print(f"Sending requests {len(reqs)}...")
    print("****************************************")
    resps = send(reqs)

    for r in resps:
        print(">>>")
        print(r.request)
        print("<<<")
        print(r)
