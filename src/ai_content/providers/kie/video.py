import asyncio
import logging
from typing import Any, Optional
from pathlib import Path
from datetime import datetime, timezone
import httpx
import json

from ai_content.core.result import GenerationResult
from ai_content.core.registry import ProviderRegistry
from ai_content.config import get_settings

logger = logging.getLogger(__name__)

@ProviderRegistry.register_video("kie")
class KieVideoProvider:
    """
    Kie AI Video Provider.
    Supports Veo 3.1, Runway, etc. via unified API.
    """

    name = "kie"
    supports_image_to_video = True
    max_duration_seconds = 10

    def __init__(self):
        self.settings = get_settings().kie

    @property
    def headers(self) -> dict[str, str]:
        """Get authorization headers."""
        return {
            "Authorization": f"Bearer {self.settings.api_key}",
            "Content-Type": "application/json",
        }

    async def generate(
        self,
        prompt: str,
        *,
        aspect_ratio: str = "16:9",
        duration_seconds: int = 5,
        first_frame_url: str | None = None,
        output_path: str | None = None,
        **kwargs: Any,
    ) -> GenerationResult:
        """
        Generate video using Kie AI.
        """
        logger.info(f"🎬 Kie AI: Generating video ({self.settings.model})")
        
        payload = {
            "model": self.settings.model,
            "prompt": prompt,
            "aspectRatio": aspect_ratio,
            "duration": duration_seconds,
            "quality": "720p",
        }

        if first_frame_url:
            payload["imageUrl"] = first_frame_url

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Correct endpoint for Veo 3.1 on Kie AI
                endpoint = f"{self.settings.base_url}/api/v1/veo/generate"
                logger.debug(f"   Kie AI Request Payload: {payload}")
                
                response = await client.post(
                    endpoint,
                    json=payload,
                    headers=self.headers,
                )
                
                logger.debug(f"   Kie AI Status Code: {response.status_code}")
                logger.debug(f"   Kie AI Response Text: {response.text}")
                
                response.raise_for_status()
                
                try:
                    result = response.json()
                except Exception as json_err:
                    logger.error(f"   Failed to parse JSON: {json_err}. Text: {response.text}")
                    return GenerationResult(
                        success=False,
                        provider=self.name,
                        content_type="video",
                        error=f"JSON parsing failed: {json_err}",
                    )

                if result is None:
                    return GenerationResult(
                        success=False,
                        provider=self.name,
                        content_type="video",
                        error="API returned None as JSON",
                    )
                
                # Extract task_id safely
                task_id = None
                if isinstance(result, dict):
                    # Check common locations for task ID
                    task_id = result.get("taskId") or result.get("task_id") or result.get("id")
                    if not task_id:
                        data = result.get("data")
                        if isinstance(data, dict):
                            task_id = data.get("taskId") or data.get("task_id") or data.get("id")
                        elif isinstance(data, str):
                            task_id = data

                if not task_id:
                    return GenerationResult(
                        success=False,
                        provider=self.name,
                        content_type="video",
                        error=f"No taskId found in response: {result}",
                    )

                logger.info(f"   Task ID: {task_id}. Polling...")
                return await self._poll_for_completion(task_id, output_path)

        except Exception as e:
            logger.error(f"Kie AI generation failed: {e}")
            return GenerationResult(
                success=False,
                provider=self.name,
                content_type="video",
                error=str(e),
            )

    async def _poll_for_completion(self, task_id: str, output_path: Optional[str] = None) -> GenerationResult:
        """Poll for task completion."""
        status_url = f"{self.settings.base_url}/api/v1/jobs/recordInfo"
        
        for attempt in range(self.settings.max_poll_attempts):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(
                        status_url,
                        params={"taskId": task_id},
                        headers=self.headers,
                    )
                    
                    if response.status_code != 200:
                        logger.warning(f"   Poll {attempt+1}: Status {response.status_code}, Body: {response.text}")
                        # If 404, maybe it's not ready yet
                        if response.status_code == 404:
                            await asyncio.sleep(self.settings.poll_interval)
                            continue
                        response.raise_for_status()

                    job = response.json()
                    logger.debug(f"   Poll {attempt+1} Result: {job}")

                data = job.get("data")
                if not data:
                    # Search result 856 said data can be null if recordInfo is empty
                    logger.info(f"   Poll {attempt+1}: Task not found yet (data is null)")
                    await asyncio.sleep(self.settings.poll_interval)
                    continue

                if not isinstance(data, dict):
                    logger.warning(f"   Poll {attempt+1}: data is not a dict: {type(data)}")
                    await asyncio.sleep(self.settings.poll_interval)
                    continue

                state = data.get("state") or data.get("status")
                logger.info(f"   Poll {attempt+1}: status={state}")

                if state in ["success", "completed", "done"]:
                    result_json = data.get("resultJson", {})
                    if isinstance(result_json, str) and result_json:
                        try:
                            result_json = json.loads(result_json)
                        except:
                            pass
                    
                    video_url = None
                    if isinstance(result_json, dict):
                        video_url = result_json.get("videoUrl") or result_json.get("url")
                    
                    if not video_url and isinstance(result_json, list) and len(result_json) > 0:
                        item = result_json[0]
                        if isinstance(item, dict):
                            video_url = item.get("url") or item.get("videoUrl")
                        else:
                            video_url = item
                    
                    # Also check main data for result
                    if not video_url:
                        video_url = data.get("videoUrl") or data.get("url")

                    if video_url:
                        logger.info(f"   Success! Downloading: {video_url}")
                        async with httpx.AsyncClient(timeout=120.0) as dl_client:
                            resp = await dl_client.get(video_url)
                            resp.raise_for_status()
                            video_data = resp.content

                        if output_path:
                            file_path = Path(output_path)
                        else:
                            output_dir = get_settings().output_dir
                            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                            file_path = output_dir / f"kie_{timestamp}.mp4"

                        file_path.parent.mkdir(parents=True, exist_ok=True)
                        file_path.write_bytes(video_data)
                        
                        return GenerationResult(
                            success=True,
                            provider=self.name,
                            content_type="video",
                            file_path=file_path,
                            data=video_data,
                            generation_id=task_id,
                            metadata={"task_id": task_id, "url": video_url}
                        )
                    return GenerationResult(
                        success=False,
                        provider=self.name,
                        content_type="video",
                        error=f"Success state but no video URL found in {job}",
                    )

                if state in ["fail", "failed", "error"]:
                    error_msg = data.get("failMsg") or data.get("error") or "Unknown error"
                    return GenerationResult(
                        success=False,
                        provider=self.name,
                        content_type="video",
                        error=f"Job failed: {error_msg}",
                    )
                
                # If still queueing or generating
                logger.debug(f"   Task is {state}...")

            except Exception as e:
                logger.warning(f"   Poll error: {e}")

            await asyncio.sleep(self.settings.poll_interval)

        return GenerationResult(
            success=False,
            provider=self.name,
            content_type="video",
            error="Polling timed out",
        )
