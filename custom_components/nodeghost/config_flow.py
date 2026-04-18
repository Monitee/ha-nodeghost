import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
import aiohttp

from .const import DOMAIN, CONF_ENDPOINT, DEFAULT_ENDPOINT

class NodeGhostConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for NodeGhost."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            api_key = user_input[CONF_API_KEY].strip()
            endpoint = user_input.get(CONF_ENDPOINT, DEFAULT_ENDPOINT).strip()

            # Validate the API key by calling the health endpoint
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{endpoint}/health",
                        timeout=aiohttp.ClientTimeout(total=10)
                    ) as resp:
                        if resp.status == 200:
                            return self.async_create_entry(
                                title="NodeGhost",
                                data={
                                    CONF_API_KEY: api_key,
                                    CONF_ENDPOINT: endpoint,
                                }
                            )
                        else:
                            errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_API_KEY): str,
                vol.Optional(CONF_ENDPOINT, default=DEFAULT_ENDPOINT): str,
            }),
            errors=errors,
        )
