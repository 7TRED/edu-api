import azure.functions as func
import logging
import json
from chatbot import get_completion_from_messages
from chatbot_teacher import get_completion_from_messages as get_completion_from_messages_teacher
from qa import answerQuery
from ytsummarizer import generate_summary

app = func.FunctionApp(http_auth_level=func.AuthLevel.ADMIN)


@app.route(route="ChatBotTrigger")
def ChatBotTrigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    response = dict()
    try:
        req_body = req.get_json()
        response_content = get_completion_from_messages(
            req_body["context"])
        response = {
            "role": "assistant",
            "content": response_content
        }

        return func.HttpResponse(
            json.dumps(response
                       ),
            status_code=200
        )

    except ValueError:
        return func.HttpResponse(json.dumps(response))


@app.route(route="QATrigger")
def QATrigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    response = dict()
    collection_name = ""  # from user
    query = ""

    try:
        req_body = req.get_json()
        collection_name = req_body["collection_name"]
        query = req_body["query"]
        response_content = answerQuery(
            query=query, collection_name=collection_name)
        response = {
            "role": "assistant",
            "content": response_content
        }

        return func.HttpResponse(
            json.dumps(response
                       ),
            status_code=200
        )

    except ValueError:
        return func.HttpResponse(json.dumps(response))


@app.route(route="YTTrigger")
def YTTrigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    response = dict()

    try:
        req_body = req.get_json()
        query = req_body["url"]
        response_content = generate_summary(query)
        response = {
            "role": "assistant",
            "content": response_content
        }

        return func.HttpResponse(
            json.dumps(response
                       ),
            status_code=200
        )

    except ValueError:
        return func.HttpResponse(json.dumps(response))


@app.route(route="ChatBotTeacherTrigger")
def ChatBotTeacherTrigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    response = dict()
    try:
        req_body = req.get_json()
        response_content = get_completion_from_messages_teacher(
            req_body["context"])
        response = {
            "role": "assistant",
            "content": response_content
        }

        return func.HttpResponse(
            json.dumps(response
                       ),
            status_code=200
        )

    except ValueError:
        return func.HttpResponse(json.dumps(response))
