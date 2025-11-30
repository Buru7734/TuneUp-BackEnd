from django.utils.deprecation import MiddlewareMixin


class RequestLoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):
        try:
            body = request.body.decode('utf-8') if request.body else ''
        except Exception:
            body = '<unreadable>'
        print(f"[RequestLoggingMiddleware] {request.method} {request.get_full_path()}")
        print("Headers:")
        for k, v in request.headers.items():
            print(f"  {k}: {v}")
        if body:
            print("Body:", body)
        return None
