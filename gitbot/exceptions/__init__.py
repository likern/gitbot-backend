import sanic.exceptions

@sanic.exceptions.add_status_code(422)
class UnprocessableEntity(sanic.exceptions.SanicException):
    pass