from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .api.v1 import products, categories, inventory, sales, auth, users, unit_types, clients, payment_methods, supplier, purchase_order, branches, role
from .database import Base, engine

#Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SuperMarket Bolivia API",
    description="API completa para sistema de supermercados en Bolivia",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://sistema-de-inventarios-tu-super.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(products.router, prefix=settings.API_V1_STR)
app.include_router(categories.router, prefix=settings.API_V1_STR)
app.include_router(inventory.router, prefix=settings.API_V1_STR)
app.include_router(sales.router, prefix=settings.API_V1_STR)
app.include_router(unit_types.router, prefix=settings.API_V1_STR)
app.include_router(clients.router, prefix=settings.API_V1_STR)
app.include_router(payment_methods.router, prefix=settings.API_V1_STR)
app.include_router(supplier.router, prefix=settings.API_V1_STR)
app.include_router(purchase_order.router, prefix=settings.API_V1_STR)
app.include_router(branches.router, prefix=settings.API_V1_STR)
app.include_router(role.router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": "Bienvenido al API de SuperMarket Bolivia"}

@app.get("/health", include_in_schema=False)
def healthcheck():
    return {"status": "healthy"}