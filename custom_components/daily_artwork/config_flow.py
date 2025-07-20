import logging
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import voluptuous as vol
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

class DailyArtworkConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    
    async def async_step_user(self, user_input=None):
        # 检查是否已有配置
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        
        # 直接创建配置条目，无需用户输入
        return self.async_create_entry(title="每日艺术与电影", data={})