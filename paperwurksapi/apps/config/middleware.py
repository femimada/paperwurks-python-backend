"""
Custom middleware for Paperwurks Backend
"""

import logging
import time
import uuid
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log incoming requests and responses.
    Adds request ID and timing information.
    """

    def process_request(self, request):
        """
        Add request ID and start time to request object
        """
        request.request_id = str(uuid.uuid4())
        request.start_time = time.time()
        
        # Log incoming request
        logger.info(
            f"[{request.request_id}] {request.method} {request.path}",
            extra={
                "request_id": request.request_id,
                "method": request.method,
                "path": request.path,
                "ip": self.get_client_ip(request),
            },
        )
        return None

    def process_response(self, request, response):
        """
        Log response with timing information
        """
        if hasattr(request, "start_time"):
            duration = time.time() - request.start_time
            request_id = getattr(request, "request_id", "unknown")
            
            # Add request ID to response headers for tracing
            response["X-Request-ID"] = request_id
            
            # Log response
            logger.info(
                f"[{request_id}] {response.status_code} {request.method} {request.path} ({duration:.3f}s)",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.path,
                    "status_code": response.status_code,
                    "duration": duration,
                },
            )
        
        return response

    def process_exception(self, request, exception):
        """
        Log exceptions
        """
        request_id = getattr(request, "request_id", "unknown")
        logger.error(
            f"[{request_id}] Exception: {exception}",
            exc_info=True,
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.path,
            },
        )
        return None

    @staticmethod
    def get_client_ip(request):
        """
        Get the client's IP address from the request
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip