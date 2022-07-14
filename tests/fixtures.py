import asyncio
import random
import string

from typing import Dict

from mlserver import MLModel
from mlserver.types import InferenceRequest, InferenceResponse, Parameters
from mlserver.codecs import NumpyCodec
from mlserver.handlers.custom import custom_handler
from mlserver.errors import MLServerError


class SumModel(MLModel):
    @custom_handler(rest_path="/my-custom-endpoint")
    async def my_payload(self, payload: list) -> int:
        return sum(payload)

    @custom_handler(rest_path="/custom-endpoint-with-long-response")
    async def long_response_endpoint(self, length: int) -> Dict[str, str]:
        alphabet = string.ascii_lowercase
        response = "".join(random.choice(alphabet) for _ in range(length))
        return {"foo": response}

    async def predict(self, payload: InferenceRequest) -> InferenceResponse:
        decoded = self.decode(payload.inputs[0])
        total = decoded.sum(axis=1, keepdims=True)

        output = NumpyCodec.encode_output(name="total", payload=total)
        response = InferenceResponse(
            id=payload.id,
            model_name=self.name,
            model_version=self.version,
            outputs=[output],
        )

        if payload.parameters and payload.parameters.headers:
            # "Echo" headers back prefixed by `x-`
            request_headers = payload.parameters.headers
            response_headers = {
                header_name: header_value
                for header_name, header_value in request_headers.items()
                if header_name.startswith("x-")
            }

            response.parameters = Parameters(headers=response_headers)

        return response


class ErrorModel(MLModel):
    error_message = "something really bad happened"

    async def predict(self, payload: InferenceRequest) -> InferenceResponse:
        raise MLServerError(self.error_message)


class SlowModel(MLModel):
    async def load(self) -> bool:
        await asyncio.sleep(10)
        self.ready = True
        return self.ready

    async def infer(self, payload: InferenceRequest) -> InferenceResponse:
        await asyncio.sleep(10)
        return InferenceResponse(id=payload.id, model_name=self.name, outputs=[])
