import time

from django.core.cache import cache
from django.http import JsonResponse


class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/admin/"):
            return self.get_response(request)

        if request.user.is_authenticated:
            if hasattr(request.user, "role") and request.user.role == "admin":
                limit = 1000
            else:
                limit = 100
            identifier = f"rate_limit_user_{request.user.id}"
        else:
            limit = 10
            identifier = f"rate_limit_ip_{self.get_client_ip(request)}"

        current_requests = cache.get(identifier, 0)

        if current_requests >= limit:
            return JsonResponse(
                {
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Limit is {limit} requests per minute.",
                },
                status=429,
            )

        cache.set(identifier, current_requests + 1, 60)

        response = self.get_response(request)
        response["X-RateLimit-Limit"] = str(limit)
        response["X-RateLimit-Remaining"] = str(limit - current_requests - 1)
        response["X-RateLimit-Reset"] = str(int(time.time()) + 60)

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip
