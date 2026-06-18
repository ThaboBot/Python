from django.http import HttpResponse


class LocalFrontendCorsMiddleware:
    allowed_origins = {
        'http://127.0.0.1:5500',
        'http://localhost:5500',
        'http://127.0.0.1:8001',
        'http://localhost:8001',
        'null',
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'OPTIONS':
            response = HttpResponse()
        else:
            response = self.get_response(request)

        origin = request.headers.get('Origin')

        if origin in self.allowed_origins:
            response['Access-Control-Allow-Origin'] = origin
            response['Access-Control-Allow-Credentials'] = 'true'
            response['Access-Control-Allow-Headers'] = 'authorization, content-type'
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'

        return response
