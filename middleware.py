from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from jose import jwt
from config import SECRET_KEY, ALGORITHM


class AuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        # Skip authentication for public routes
        public_routes = ["/login", "/register", "/health"]

        if request.url.path in public_routes:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            request.state.user = None
            return await call_next(request)

        try:
            token = auth_header.split(" ")[1]

            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            request.state.user = payload

        except Exception:
            request.state.user = None

        response = await call_next(request)

        return response