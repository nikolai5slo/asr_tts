import homeassistant.helpers.config_validation as cv
import voluptuous as vol
from homeassistant.config_entries import ConfigFlow

from . import DOMAIN

class ConfigFlowHandler(ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None, errors=None):
        if user_input:
            return self.async_create_entry(title="ASR TTS", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("api_url", default="https://slovenscina.eu/api/translator/asr"): cv.string,
                    vol.Required("language", default="sl_SI"): cv.string,
                },
            ),
            errors=errors,
        )
