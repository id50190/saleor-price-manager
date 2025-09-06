from fastapi import APIRouter, Depends, HTTPException
from app.models.schemas import ChannelMarkup
from app.services.markup_service import markup_service
from app.core.security import verify_token

router = APIRouter()

@router.get("/")
async def list_channels(token: str = Depends(verify_token)):
    """Получить список всех каналов с их наценками"""
    from app.saleor.api import list_channels
    
    channels = await list_channels()
    
    # Добавляем информацию о наценках
    result = []
    for channel in channels:
        markup = await markup_service.get_channel_markup(channel["id"])
        channel["markup_percent"] = markup
        result.append(channel)
        
    return result

@router.post("/markup")
async def set_markup(markup: ChannelMarkup, token: str = Depends(verify_token)):
    """Установить наценку для канала"""
    success = await markup_service.set_channel_markup(
        markup.channel_id, markup.markup_percent
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to update channel markup")
        
    return {"success": True, "markup": markup}
