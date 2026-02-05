from logging import Filter, LogRecord

from middleware.requests import request_id_var


class RequestIDFilter(Filter):
    def filter(self, record: LogRecord) -> bool:
        record.request_id = request_id_var.get("")
        return True
