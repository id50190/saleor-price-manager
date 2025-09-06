import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response, Query 
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.api import channels, prices, webhooks
from app.core.config import settings
from app.saleor.client import init_saleor_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_saleor_client()
    yield
    # Shutdown - можно добавить cleanup логику если нужно
    pass

app = FastAPI(
  title='Saleor Price Manager',
  description='FastAPI service for managing dynamic pricing across multiple Saleor channels with percentage-based markups and Redis caching',
  version='1.0.0',
  docs_url='/docs',                   # Путь для Swagger UI
  redoc_url='/redoc',                 # Путь для ReDoc
  openapi_url='/api/v1/openapi.json', # Путь для OpenAPI-схемы
  lifespan=lifespan)

# Middleware
app.add_middleware(
  CORSMiddleware,
  allow_origins=settings.CORS_ORIGINS,
  allow_credentials=True,
  allow_methods=['*'],
  allow_headers=['*'])

@app.middleware('http')
async def add_process_time_header(request: Request, call_next):
  start_time = time.time()
  response = await call_next(request)
  process_time = time.time() - start_time
  if request.query_params.__contains__('set-process-time'):
    response.headers['X-Process-Time'] = str(process_time)
  return response

# Include routers
app.include_router(channels.router, prefix='/api/channels', tags=['channels'])
app.include_router(prices.router,   prefix='/api/prices',   tags=['prices'])
app.include_router(webhooks.router, prefix='/webhooks',     tags=['webhooks'])

@app.get('/health')
async def health_check():
  return {'status': 'ok'}
