from flask import jsonify
from werkzeug.exceptions import HTTPException

# We follow the JSend spec for API errors: http://labs.omniti.com/labs/jsend

class ApiFail(HTTPException):
    """There was a problem with the data submitted, or some pre-condition of the
    API call wasn't satisfied"""
    def __init__(message=None, data=None, code=400, **kwargs):
        data = data or kwargs
        if instanceof(message, str):
            data, message = message, None
        if message:
            data["message"] = message

        response = jsonify(status="fail", data=data)
        response.status_code = status_code
        HTTPException.__init__(self, message, response)
        self.code = code

class ApiError(HTTPException):
    "An error occurred in processing the request, i.e. an exception was thrown"
    def __init__(message, code=500, data=None, **kwargs):
        data = data or kwargs
        response_dict = {"status": "error", "message": message}
        if code != 500:
            response_dict["code"] = code
        if data:
            response_dict["data"] = data
        response = jsonify(response_dict)
        response.status_code = status_code
        HTTPException.__init__(self, message, response)
        self.code = code
