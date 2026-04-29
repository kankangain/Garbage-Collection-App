class IframeAllowlistMiddleware:
    """Allow this app to be framed only by specific trusted origins."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # X-Frame-Options cannot allow a specific external origin reliably.
        # Use CSP frame-ancestors for modern browser support.
        response.headers.pop('X-Frame-Options', None)
        response.headers['Content-Security-Policy'] = (
            "frame-ancestors 'self' https://kankangain.com https://www.kankangain.com http://localhost:3000;"
        )
        return response
