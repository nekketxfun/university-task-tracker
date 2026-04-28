from .context import set_request

class AuditRequestMiddleware:
    """Привязывает текущий HTTP-запрос к потоку для доступа в сигналах"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        set_request(request)
        return self.get_response(request)