"""
Django Ninja API configuration for Paperwurks Backend
"""

from ninja import NinjaAPI
from ninja.responses import Response
from django.conf import settings


api = NinjaAPI(
    title="Paperwurks API",
    version="1.0.0",
    description="Property due diligence and document management platform",
    docs_url="/docs" if settings.DEBUG else None,  
)


# Health check endpoint (no authentication required)
@api.get("/health", tags=["System"], auth=None)
def health_check(request):
    """
    Health check endpoint for load balancers and monitoring.
    Returns 200 OK if the service is healthy.
    """
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
    }


# Version endpoint
@api.get("/version", tags=["System"], auth=None)
def version(request):
    """Get API version information"""
    return {
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "debug": settings.DEBUG,
    }


# Import and register routers from apps
# Note: These imports will be added as we create the apps

# Example structure (uncomment as apps are created):
# from apps.users.api import router as users_router
# from apps.properties.api import router as properties_router
# from apps.documents.api import router as documents_router
# from apps.packs.api import router as packs_router
# from apps.searches.api import router as searches_router

# api.add_router("/users/", users_router, tags=["Users"])
# api.add_router("/properties/", properties_router, tags=["Properties"])
# api.add_router("/documents/", documents_router, tags=["Documents"])
# api.add_router("/packs/", packs_router, tags=["Packs"])
# api.add_router("/searches/", searches_router, tags=["Searches"])


# Global exception handler
@api.exception_handler(Exception)
def handle_exception(request, exc):
    """
    Global exception handler for unhandled exceptions.
    Logs the error and returns a generic error response.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    if settings.DEBUG:
        return Response(
            {"error": "Internal server error", "detail": str(exc)},
            status=500,
        )
    
    return Response(
        {"error": "Internal server error"},
        status=500,
    )