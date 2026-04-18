import logging
import aiohttp
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY

from .const import DOMAIN, CONF_ENDPOINT, DEFAULT_ENDPOINT

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up NodeGhost from a config entry."""
    api_key = entry.data[CONF_API_KEY]
    endpoint = entry.data.get(CONF_ENDPOINT, DEFAULT_ENDPOINT)

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "api_key": api_key,
        "endpoint": endpoint,
    }

    async def handle_remember(call: ServiceCall) -> None:
        """Handle the nodeghost.remember service call."""
        text = call.data.get("text", "").strip()
        namespace = call.data.get("namespace", "default")

        if not text:
            _LOGGER.warning("NodeGhost remember called with empty text")
            return

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        payload = {
            "text": text,
            "namespace": namespace,
            "owner_token": api_key,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{endpoint}/v1/memory/store",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status == 200:
                        _LOGGER.debug("NodeGhost stored memory: %s", text)
                    else:
                        _LOGGER.error("NodeGhost memory store failed: %s", resp.status)
        except Exception as err:
            _LOGGER.error("NodeGhost remember error: %s", err)

    async def handle_recall(call: ServiceCall) -> None:
        """Handle the nodeghost.recall service call."""
        query = call.data.get("query", "").strip()
        namespace = call.data.get("namespace", "default")

        if not query:
            _LOGGER.warning("NodeGhost recall called with empty query")
            return

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        payload = {
            "query": query,
            "namespace": namespace,
            "owner_token": api_key,
            "topK": 5,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{endpoint}/v1/memory/recall",
                    json=payload,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        memories = data.get("memories", [])
                        _LOGGER.debug("NodeGhost recalled %d memories", len(memories))
                        # Fire an event with the recalled memories
                        hass.bus.async_fire(
                            "nodeghost_recall_result",
                            {"query": query, "memories": memories}
                        )
                    else:
                        _LOGGER.error("NodeGhost recall failed: %s", resp.status)
        except Exception as err:
            _LOGGER.error("NodeGhost recall error: %s", err)

    hass.services.async_register(DOMAIN, "remember", handle_remember)
    hass.services.async_register(DOMAIN, "recall", handle_recall)

    _LOGGER.info("NodeGhost integration loaded successfully")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.services.async_remove(DOMAIN, "remember")
    hass.services.async_remove(DOMAIN, "recall")
    hass.data[DOMAIN].pop(entry.entry_id)
    return True
