from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import (DOMAIN, SENSOR_NAME, SENSOR_ICON, NEW_SENSOR_NAME, NEW_SENSOR_ICON, QUOTE_SENSOR_NAME, QUOTE_SENSOR_ICON,
    MOVIE_SENSOR_NAME, MOVIE_SENSOR_ICON, ATTR_MOV_TITLE, ATTR_MOV_AREA, ATTR_MOV_DIRECTOR, ATTR_MOV_YEAR, ATTR_MOV_TYPE,
    ATTR_MOV_RATING, ATTR_MOV_INTRO, ATTR_MOV_TEXT, ATTR_MOV_PIC, ATTR_POSTER_URL, ATTR_MOV_LINK, ATTR_DATE, ATTR_BG_COLOR, ATTR_COLOR)

class DailyArtworkSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "daily_artwork"
    _attr_icon = SENSOR_ICON

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{config_entry.entry_id}_artwork"

    @property
    def state(self):
        data = self.coordinator.data or {}
        return data.get("name", "未知作品")

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data or {}
        return {
            "img": data.get("image", ""),
            "aut": data.get("author", "未知作者"),
            "text": data.get("text", "")
        }

class DailyArtworkNewSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "daily_artwork_new"
    _attr_icon = NEW_SENSOR_ICON

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{config_entry.entry_id}_new_artwork"

    @property
    def state(self):
        if self.coordinator.data is None:
            return ""
        return self.coordinator.data.get("titleDetail", "未知标题")

    @property
    def extra_state_attributes(self):
        if self.coordinator.data is None:
            return {}
        return {
            "image": self.coordinator.data.get("img", ""),
            "author": self.coordinator.data.get("author", "未知作者"),
            "description": self.coordinator.data.get("content", "")
        }

class DailyQuoteSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "daily_quote"
    _attr_icon = QUOTE_SENSOR_ICON

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{config_entry.entry_id}_quote"

    @property
    def state(self):
        if self.coordinator.data is None:
            return ""
        return self.coordinator.data.get("content", "")

    @property
    def extra_state_attributes(self):
        if self.coordinator.data is None:
            return {}
        return {
            "content": self.coordinator.data.get("content", ""),
            "from": self.coordinator.data.get("from", ""),
            "author": self.coordinator.data.get("author", ""),
            "pic_url": self.coordinator.data.get("pic_url", ""),
            "thumb": self.coordinator.data.get("thumb", "")
        }

class DailyMovieSensor(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "daily_movie"
    _attr_icon = MOVIE_SENSOR_ICON

    def __init__(self, coordinator, config_entry):
        super().__init__(coordinator)
        self._attr_unique_id = f"{config_entry.entry_id}_movie"

    @property
    def state(self):
        data = self.coordinator.data or {}
        return data.get(ATTR_MOV_TITLE, "未知电影")

    @property
    def extra_state_attributes(self):
        data = self.coordinator.data or {}
        return {
            ATTR_MOV_AREA: data.get(ATTR_MOV_AREA, ""),
            ATTR_MOV_DIRECTOR: data.get(ATTR_MOV_DIRECTOR, ""),
            ATTR_MOV_YEAR: data.get(ATTR_MOV_YEAR, ""),
            ATTR_MOV_TYPE: data.get(ATTR_MOV_TYPE, ""),
            ATTR_MOV_RATING: data.get(ATTR_MOV_RATING, ""),
            ATTR_MOV_INTRO: data.get(ATTR_MOV_INTRO, ""),
            ATTR_MOV_TEXT: data.get(ATTR_MOV_TEXT, ""),
            ATTR_MOV_PIC: data.get(ATTR_MOV_PIC, ""),
            ATTR_POSTER_URL: data.get(ATTR_POSTER_URL, ""),
            ATTR_MOV_LINK: data.get(ATTR_MOV_LINK, ""),
            ATTR_DATE: data.get(ATTR_DATE, ""),
            ATTR_BG_COLOR: data.get(ATTR_BG_COLOR, ""),
            ATTR_COLOR: data.get(ATTR_COLOR, "")
        }

async def async_setup_entry(hass, config_entry, async_add_entities):
    coordinator_old = hass.data[DOMAIN][f"{config_entry.entry_id}_old"]
    coordinator_new = hass.data[DOMAIN][f"{config_entry.entry_id}_new"]
    coordinator_quote = hass.data[DOMAIN][f"{config_entry.entry_id}_quote"]
    coordinator_movie = hass.data[DOMAIN][f"{config_entry.entry_id}_movie"]
    async_add_entities([
        DailyArtworkSensor(coordinator_old, config_entry),
        DailyArtworkNewSensor(coordinator_new, config_entry),
        DailyQuoteSensor(coordinator_quote, config_entry),
        DailyMovieSensor(coordinator_movie, config_entry)
    ])