from .auth_router import router as auth_router
from .closet_router import router as closet_router
from .outfit_router import router as outfit_router
from .favorite_router import router as favorite_router

__all__ = [
    "auth_router",
    "closet_router",
    "outfit_router",
    "favorite_router",
]

