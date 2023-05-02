import json
import logging
import openai
from flask import Flask, request, Response, stream_with_context
from flask_restful import Resource, Api, abort
from config import config, configure_logging


# Initialize Flask app and RESTful API
app = Flask(__name__)
api = Api(app)
app.config.from_object(config)
configure_logging(config)


def get_bearer_token(req):
    auth_header = req.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        bearer_token = auth_header[7:]
        return bearer_token
    return None


class OpenAIModels(Resource):
    def get(self):
        try:
            openai.api_key = get_bearer_token(request)
            models = openai.Model.list()
            logging.info("Successfully retrieved models")
            return models, 200
        except Exception as err:
            logging.info("Error: %s", str(err))
            abort(500, message=str(err))


class GPT3Conversation(Resource):
    def post(self):
        data = request.get_json(force=True)
        messages = data.get("messages", [])
        try:
            openai.api_key = get_bearer_token(request)

            response = openai.ChatCompletion.create(
                model=data.get("model", "gpt-3.5-turbo"),
                max_tokens=data.get("max_tokens", 150),
                n=data.get("n", 1),
                stop=data.get("stop", ""),
                temperature=data.get("temperature", 0.5),
                stream=data.get("stream", True),
                messages=messages,
            )

            def generate():
                for chunk in response:
                    yield f"data: {json.dumps(chunk)}\n\n".encode("utf-8")

            return Response(
                stream_with_context(generate()),
                content_type="text/event-stream",
            )
        except Exception as err:
            logging.info("Error: %s", str(err))
            abort(500, message=str(err))


api.add_resource(GPT3Conversation, "/v1/chat/completions")
api.add_resource(OpenAIModels, "/v1/models")

if __name__ == "__main__":
    app.run(debug=True)
