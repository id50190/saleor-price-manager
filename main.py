import time

from fastapi import FastAPI, Request, Response, Query 
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from app.api import channels, prices, webhooks
from app.core.config import settings
from app.saleor.client import init_saleor_client

app = FastAPI(
  title='Saleor Price Manager',
  description='Service for managing pricing across multiple Saleor channels',
  version='1.0.0',
  docs_url='/docs',                   # Путь для Swagger UI
  redoc_url='/redoc',                 # Путь для ReDoc
  openapi_url='/api/v1/openapi.json') # Путь для OpenAPI-схемы

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

# Startup event
@app.on_event('startup')
async def startup_event():
  await init_saleor_client()

# Include routers
app.include_router(channels.router, prefix='/api/channels', tags=['channels'])
app.include_router(prices.router,   prefix='/api/prices',   tags=['prices'])
app.include_router(webhooks.router, prefix='/webhooks',     tags=['webhooks'])

@app.get('/health')
async def health_check():
  return {'status': 'ok'}
