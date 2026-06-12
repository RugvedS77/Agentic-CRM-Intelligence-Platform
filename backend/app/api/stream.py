from fastapi import APIRouter, Query
from fastapi.responses import StreamingResponse
from datetime import datetime
import asyncio
import json
from pathlib import Path

from app.core.database import SessionLocal
from app.models.email_model import Email
from app.models.thread_model import Thread

router = APIRouter(tags=["Streaming"])

DATASET_PATH = Path(__file__).resolve().parent.parent / "scripts" / "email-data-advanced.json"

# Global streaming state
streaming_state = {
    "is_streaming": False,
    "current_index": 0,
    "total_emails": 0,
    "inserted": 0,
    "duplicates": 0
}


def calculate_delay_ms(speed: int) -> float:
    """Convert speed (1-100) to delay in seconds.
    Speed 1 = 1 email per second (1000ms delay)
    Speed 100 = 100 emails per second (10ms delay)
    """
    if speed <= 0:
        return 0.01
    if speed >= 100:
        return 0.01
    return max(0.01, 1.0 / speed)


@router.post("/api/stream/start")
async def start_stream(
    speed: int = Query(1, ge=1, le=100)
):
    global streaming_state
    
    # Reset state
    streaming_state = {
        "is_streaming": True,
        "current_index": 0,
        "total_emails": 0,
        "inserted": 0,
        "duplicates": 0
    }
    
    try:
        with open(DATASET_PATH, "r", encoding="utf-8") as f:
            emails = json.load(f)
    except FileNotFoundError:
        return {
            "status": "error",
            "message": "Dataset file not found."
        }
    
    streaming_state["total_emails"] = len(emails)
    delay = calculate_delay_ms(speed)
    
    async def stream_emails():
        global streaming_state
        
        for i, item in enumerate(emails):
            if not streaming_state["is_streaming"]:
                break
            
            streaming_state["current_index"] = i + 1
            
            # Create a new session for each iteration
            db = SessionLocal()
            try:
                existing = (
                    db.query(Email)
                    .filter(Email.message_id == item["message_id"])
                    .first()
                )
                
                if existing:
                    streaming_state["duplicates"] += 1
                else:
                    thread = (
                        db.query(Thread)
                        .filter(Thread.thread_id == item["thread_id"])
                        .first()
                    )
                    
                    if not thread:
                        thread = Thread(
                            thread_id=item["thread_id"],
                            subject=item["subject"],
                            sender_email=item["sender"],
                            first_seen_at=datetime.fromisoformat(
                                item["timestamp"].replace("Z", "+00:00")
                            ),
                            last_updated_at=datetime.fromisoformat(
                                item["timestamp"].replace("Z", "+00:00")
                            ),
                        )
                        db.add(thread)
                        db.flush()
                    
                    email = Email(
                        message_id=item["message_id"],
                        sender=item["sender"],
                        subject=item["subject"],
                        body=item["body"],
                        timestamp=datetime.fromisoformat(
                            item["timestamp"].replace("Z", "+00:00")
                        ),
                        thread_id=thread.id,
                    )
                    db.add(email)
                    streaming_state["inserted"] += 1
                
                db.commit()
            finally:
                db.close()
            
            # Yield progress update
            yield f"data: {json.dumps({
                'type': 'progress',
                'current': streaming_state['current_index'],
                'total': streaming_state['total_emails'],
                'inserted': streaming_state['inserted'],
                'duplicates': streaming_state['duplicates'],
                'email': item.get('subject', '')[:50]
            })}\n\n"
            
            # Apply delay based on speed
            await asyncio.sleep(delay)
        
        streaming_state["is_streaming"] = False
        yield f"data: {json.dumps({
            'type': 'complete',
            'inserted': streaming_state['inserted'],
            'duplicates': streaming_state['duplicates']
        })}\n\n"
    
    return StreamingResponse(stream_emails(), media_type="text/plain")


@router.post("/api/stream/stop")
async def stop_stream():
    global streaming_state
    streaming_state["is_streaming"] = False
    return {"status": "stopped", "message": "Streaming stopped by user."}


@router.get("/api/stream/status")
async def stream_status():
    global streaming_state
    return {
        "is_streaming": streaming_state["is_streaming"],
        "current_index": streaming_state["current_index"],
        "total_emails": streaming_state["total_emails"],
        "inserted": streaming_state["inserted"],
        "duplicates": streaming_state["duplicates"]
    }
