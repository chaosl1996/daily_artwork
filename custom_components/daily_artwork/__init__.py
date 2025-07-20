# 导入异步编程相关模块
import asyncio
# 导入日志记录模块
import logging
# 导入日期时间相关模块
from datetime import datetime, timedelta
# 从Home Assistant配置项模块导入配置项类
from homeassistant.config_entries import ConfigEntry
# 从Home Assistant核心模块导入HomeAssistant类
from homeassistant.core import HomeAssistant
# 从Home Assistant协调器模块导入数据更新协调器和更新失败异常类
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
# 导入异步HTTP请求库
import aiohttp
# 从BeautifulSoup库导入HTML解析器
from bs4 import BeautifulSoup
# 从常量模块导入所需的常量
from .const import (
    RESOURCE_URL_TEMPLATE_QUOTE,
    DOMAIN, LOGIN_URL, RESOURCE_URL_TEMPLATE_OLD, RESOURCE_URL_TEMPLATE_NEW, CDN_PREFIX, THUMB_SUFFIX,
    RESOURCE_URL_MOVIE, USER_AGENT, SIGNATURE_KEY, ORIGIN, SEC_FETCH_MODE, SEC_FETCH_SITE,
    ATTR_MOV_TITLE, ATTR_MOV_AREA, ATTR_MOV_DIRECTOR, ATTR_MOV_YEAR, ATTR_MOV_TYPE,
    ATTR_MOV_RATING, ATTR_MOV_INTRO, ATTR_MOV_TEXT, ATTR_MOV_PIC, ATTR_POSTER_URL,
    ATTR_MOV_LINK, ATTR_DATE, ATTR_BG_COLOR, ATTR_COLOR
)

# 创建日志记录器实例
_LOGGER = logging.getLogger(__name__)

# 定义艺术品数据更新协调器类，继承自DataUpdateCoordinator
class ArtworkDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, logger, url_template, api_type, requires_auth=True):
        super().__init__(
            hass,
            logger,
            name=DOMAIN,
            update_interval=timedelta(hours=3),
        )
        # 初始化认证令牌
        self.token = None
        # 初始化资源URL模板
        self.url_template = url_template
        # 初始化API类型
        self.api_type = api_type
        # 初始化是否需要认证标志
        self.requires_auth = requires_auth
        # 初始化数据为空字典，避免NoneType错误
        self.data = {}  # 初始化为空字典，避免NoneType错误

    # 异步更新数据的方法
    async def _async_update_data(self):
        try:
            # 1. 获取token (仅当需要认证时)
            if self.requires_auth and not self.token:
                await self._async_login()
                if not self.token:
                    raise UpdateFailed("无法获取登录token")

            # 2. 获取资源数据
            resource_url = self.url_template
            # 仅当URL模板包含{}时才使用日期格式化
            if "{}" in resource_url:
                date_str = datetime.now().strftime("%Y-%m-%d")
                resource_url = resource_url.format(date_str)
            
            data = await self._async_fetch_resource(resource_url)

            # 检查数据是否为空
            if data is None:
                _LOGGER.error("API返回空数据，api_type: %s", self.api_type)
                raise UpdateFailed("API返回空数据")
            # 验证数据类型为字典
            if not isinstance(data, dict):
                _LOGGER.error("API返回数据格式错误，预期字典类型，实际类型: %s, api_type: %s", type(data), self.api_type)
                raise UpdateFailed("API返回数据格式错误")

            # 3. 根据API类型处理数据
            if self.api_type == "old":
                try:
                    # 新的旧传感器API (getdailyart)
                    # 提取基本信息
                    name = data.get("name", "未知作品")
                    image_url = data.get("image", "")
                    authors = data.get("authors", [{}])
                    # 安全获取作者信息
                    if isinstance(authors, list) and len(authors) > 0 and isinstance(authors[0], dict):
                        author = authors[0].get("name", "未知作者")
                    else:
                        author = "未知作者"
                    
                    # 处理作品描述：取前四行
                    description = data.get("description", "")
                    lines = description.split('\n')[:4]  # 取前四行
                    processed_text = '\n'.join(lines).strip()
                    
                    return {
                        "name": name,
                        "image": image_url,
                        "author": author,
                        "text": processed_text
                    }
                except Exception as e:
                    _LOGGER.error("旧传感器数据处理失败: %s", str(e))
                    return {}
            elif self.api_type == "quote":
                try:
                    # 每日一言API数据处理
                    # 获取并验证data字段为字典
                    raw_quote_data = data.get("data", {})
                    quote_data = raw_quote_data if isinstance(raw_quote_data, dict) else {}
                    
                    return {
                        "content": quote_data.get("content", ""),
                        "from": quote_data.get("from", ""),
                        "author": quote_data.get("author", ""),
                        "pic_url": quote_data.get("pic_url", ""),
                        "thumb": quote_data.get("thumb", "")
                    }
                except Exception as e:
                    _LOGGER.error("每日一言数据处理失败: %s", str(e))
                    return {}
            elif self.api_type == "movie":
                try:
                    # 检查API返回状态
                    if data.get("code") != 200:
                        _LOGGER.error("电影API请求失败，错误码: %s, 错误信息: %s", data.get("code"), data.get("msg"))
                        raise UpdateFailed(f"电影API请求失败: {data.get('msg', '未知错误')}")

                    # 提取电影数据
                    movie_data = data.get("data", {})
                    if not isinstance(movie_data, dict):
                        _LOGGER.error("电影数据格式错误，预期字典类型，实际类型: %s", type(movie_data))
                        raise UpdateFailed("电影数据格式错误")

                    # 映射电影数据到传感器属性
                    return {
                        ATTR_MOV_TITLE: movie_data.get(ATTR_MOV_TITLE, "未知电影"),
                        ATTR_MOV_AREA: movie_data.get(ATTR_MOV_AREA, ""),
                        ATTR_MOV_DIRECTOR: movie_data.get(ATTR_MOV_DIRECTOR, ""),
                        ATTR_MOV_YEAR: movie_data.get(ATTR_MOV_YEAR, ""),
                        ATTR_MOV_TYPE: movie_data.get(ATTR_MOV_TYPE, ""),
                        ATTR_MOV_RATING: movie_data.get(ATTR_MOV_RATING, ""),
                        ATTR_MOV_INTRO: movie_data.get(ATTR_MOV_INTRO, ""),
                        ATTR_MOV_TEXT: movie_data.get(ATTR_MOV_TEXT, ""),
                        ATTR_MOV_PIC: movie_data.get(ATTR_MOV_PIC, ""),
                        ATTR_POSTER_URL: movie_data.get(ATTR_POSTER_URL, ""),
                        ATTR_MOV_LINK: movie_data.get(ATTR_MOV_LINK, ""),
                        ATTR_DATE: movie_data.get(ATTR_DATE, ""),
                        ATTR_BG_COLOR: movie_data.get(ATTR_BG_COLOR, ""),
                        ATTR_COLOR: movie_data.get(ATTR_COLOR, "")
                    }
                except Exception as e:
                    _LOGGER.error("电影数据处理失败: %s", str(e))
                    return {}
            else:
                try:
                    # 现有的新传感器API (arrrt)
                    # 3. 处理图片URL
                    data_dict = data.get("data", {})
                    if isinstance(data_dict, dict):
                        img_original = data_dict.get("img")
                        if isinstance(img_original, str) and img_original.endswith(THUMB_SUFFIX):
                            img_processed = img_original[:-len(THUMB_SUFFIX)]
                            data_dict["img"] = CDN_PREFIX + img_processed

                        # 4. 处理HTML内容
                        content_html = data.get("data", {}).get("content", "")
                        if content_html:
                            soup = BeautifulSoup(content_html, "html.parser")
                            # 删除指定文本
                            text_to_remove = "画作介绍由 Arrrt 团队撰写，转载需获得书面授权许可；如对内容有疑问或建议，或您认为涉及侵犯您的权益，请和我们联系。"
                            for element in soup.find_all(string=lambda text: text and text_to_remove in text):
                                element.replace_with(element.replace(text_to_remove, ''))
                            data["data"]["content"] = soup.get_text(separator="\n")

                        return data.get("data", {})

                    return data_dict
                except Exception as e:
                    _LOGGER.error("新传感器数据处理失败: %s", str(e))
                    return {}

        except Exception as e:
            # 仅当需要认证时重置token
            if self.requires_auth:
                self.token = None  # 重置token，下次更新时重新登录
            # 确保数据不为None
            self.data = {}
            raise UpdateFailed(f"数据更新失败: {str(e)}") from e

    # 异步登录方法，用于获取认证token
    async def _async_login(self):
        try:
            # 定义登录请求头
            login_headers = {
                "Host": "arrrt.wedea.cn",
                "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
                "Accept": "*/*",
                "Connection": "keep-alive",
                "User-Agent": "Arrrt_FE_iOS/1.1.5 (cn.wedea.arrrt; build:33; iOS 19.0.0) Alamofire/5.6.1",
                "Accept-Language": "zh-Hans-CN;q=1.0, en-CN;q=0.9",
                "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
            }

            # 定义登录请求数据
            login_data = {
                "deviceToken": "2f7d0ccffbe183ae7dcc1da3242747a30ab4893abc337d14f4421f636bebc300",
                "deviceType": "IOS",
                "uuid": "CF61CEF6-AF6E-4C5C-A060-14C1C54A87E1"
            }

            # 使用异步HTTP会话发送登录请求
            async with aiohttp.ClientSession() as session:
                async with session.post(LOGIN_URL, headers=login_headers, data=login_data) as response:
                    response.raise_for_status()
                    result = await response.json()
                    self.token = result.get("data", {}).get("token")
        except Exception as e:
            raise UpdateFailed(f"登录失败: {str(e)}") from e

    # 异步获取资源数据的方法
    async def _async_fetch_resource(self, url):
        headers = {}
        # 为每日一言API添加必要请求头
        if self.api_type == "quote":
            headers = {
                "User-Agent": USER_AGENT,
                "Signaturekey": SIGNATURE_KEY,
                "Origin": ORIGIN,
                "Sec-Fetch-Mode": SEC_FETCH_MODE,
                "Sec-Fetch-Site": SEC_FETCH_SITE,
                "Accept": "application/json, text/plain, */*"
            }
        # 为电影API添加必要请求头
        elif self.api_type == "movie":
            headers = {
                "User-Agent": USER_AGENT,
                "Signaturekey": SIGNATURE_KEY,
                "Origin": ORIGIN,
                "Sec-Fetch-Mode": SEC_FETCH_MODE,
                "Sec-Fetch-Site": SEC_FETCH_SITE,
                "Accept": "application/json, text/plain, */*"
            }
        if self.requires_auth:
            headers["authorization"] = self.token
        if self.api_type == "old":
            headers["lang"] = "zh-Hans-CN"
        
        # 使用异步HTTP会话发送资源请求
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                response.raise_for_status()
                return await response.json()

# 异步设置配置项的方法
async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # 初始化领域数据存储
    hass.data.setdefault(DOMAIN, {})
    
    # 创建电影协调器
    coordinator_movie = ArtworkDataUpdateCoordinator(
        hass, 
        _LOGGER, 
        url_template=RESOURCE_URL_MOVIE, 
        api_type="movie", 
        requires_auth=False
    )
    coordinator_movie.update_interval = timedelta(hours=24)
    await coordinator_movie.async_config_entry_first_refresh()

    # 存储电影协调器实例
    hass.data[DOMAIN][f"{entry.entry_id}_movie"] = coordinator_movie

    # 创建其他协调器实例
    # 旧版艺术品协调器
    coordinator_old = ArtworkDataUpdateCoordinator(
        hass, _LOGGER, url_template=RESOURCE_URL_TEMPLATE_OLD, api_type="old"
    )
    await coordinator_old.async_config_entry_first_refresh()

    # 新版艺术品协调器
    coordinator_new = ArtworkDataUpdateCoordinator(
        hass, _LOGGER, url_template=RESOURCE_URL_TEMPLATE_NEW, api_type="new"
    )
    await coordinator_new.async_config_entry_first_refresh()

    # 名言协调器
    coordinator_quote = ArtworkDataUpdateCoordinator(
        hass, _LOGGER, url_template=RESOURCE_URL_TEMPLATE_QUOTE, api_type="quote", requires_auth=False
    )
    await coordinator_quote.async_config_entry_first_refresh()

    # 存储所有协调器实例
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][f"{entry.entry_id}_old"] = coordinator_old
    hass.data[DOMAIN][f"{entry.entry_id}_new"] = coordinator_new
    hass.data[DOMAIN][f"{entry.entry_id}_quote"] = coordinator_quote

    # 转发配置项设置到传感器平台
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True
    # 创建两个独立的协调器实例，使用不同的URL模板
    coordinator_old = ArtworkDataUpdateCoordinator(
        hass, _LOGGER, 
        url_template=RESOURCE_URL_TEMPLATE_OLD,
        api_type="old",
        requires_auth=False
    )
    coordinator_new = ArtworkDataUpdateCoordinator(
        hass, _LOGGER, 
        url_template=RESOURCE_URL_TEMPLATE_NEW,
        api_type="new",
        requires_auth=True
    )
    coordinator_quote = ArtworkDataUpdateCoordinator(
        hass, _LOGGER, 
        url_template=RESOURCE_URL_TEMPLATE_QUOTE,
        api_type="quote",
        requires_auth=False
    )
    
    # 初始化两个协调器的数据
    await asyncio.gather(
        coordinator_old.async_config_entry_first_refresh(),
        coordinator_new.async_config_entry_first_refresh(),
        coordinator_quote.async_config_entry_first_refresh()
    )
    
    # 存储两个协调器实例
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][f"{entry.entry_id}_old"] = coordinator_old
    hass.data[DOMAIN][f"{entry.entry_id}_new"] = coordinator_new
    hass.data[DOMAIN][f"{entry.entry_id}_quote"] = coordinator_quote

    # 转发配置项设置到传感器平台
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

# 异步卸载配置项的方法
async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = all(
        await asyncio.gather(
            hass.config_entries.async_forward_entry_unload(entry, "sensor"),
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok

# 定义集成的域名
DOMAIN = "daily_artwork"