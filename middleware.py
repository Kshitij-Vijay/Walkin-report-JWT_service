from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse
from jose import jwt
from config import SECRET_KEY, ALGORITHM


class AuthMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        public_routes = ["/login", "/register", "/health"]

        # Allow public routes without authentication
        if request.url.path in public_routes:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication required"}
            )

        try:
            token = auth_header.split(" ")[1]

            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            request.state.user = payload

        except Exception:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired token"}
            )

        response = await call_next(request)

        return response