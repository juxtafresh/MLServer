from mlserver import types, MLModel


class SumModel(MLModel):
    async def predict(self, payload: types.InferenceRequest) -> types.InferenceResponse:
        total = sum(sum(inp.data) for inp in payload.inputs)
        output = types.ResponseOutput(
            name="total", shape=[1], datatype="FP32", data=[total]
        )
        return types.InferenceResponse(model_name=self.name, id="1", outputs=[output])
