import logging
import time

logger = logging.getLogger('apps')


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)
        duration = (time.time() - start) * 1000
        logger.info(
            f"{request.method} {request.path} → {response.status_code} ({duration:.1f}ms)"
        )
        return response
