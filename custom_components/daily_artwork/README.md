# 每日艺术与电影 (Daily Art and Movie)

Home Assistant集成，集成每日名画和每日电影功能，自动获取艺术作品和电影信息并在Home Assistant中显示。

## 功能特点

- 每日名画1：获取最新艺术作品信息
- 每日名画2：获取经典名画信息
- 每日一言：获取每日名言警句
- 每日电影：获取每日精选电影信息

## 安装方法

### 手动安装

1. 下载最新发布的zip文件
2. 解压到Home Assistant的`config/custom_components/daily_artwork`目录
3. 重启Home Assistant
4. 在集成页面添加"每日艺术与电影"

## 配置

1. 在Home Assistant中，进入**配置 > 集成 > 添加集成**
2. 搜索"每日艺术与电影"并选择
3. 按照提示完成配置（通常无需额外设置）

## 传感器实体

| 实体ID | 名称 | 描述 |
|--------|------|------|
| sensor.daily_artwork_new | 每日名画1 | 最新艺术作品信息 |
| sensor.daily_artwork_old | 每日名画2 | 经典名画信息 |
| sensor.daily_quote | 每日一言 | 每日名言警句 |
| sensor.daily_movie | 每日电影 | 每日精选电影信息 |

## 故障排除

- 确保网络连接正常
- 检查API请求是否被防火墙阻止
- 查看Home Assistant日志获取详细错误信息

## 致谢

- 感谢提供API的服务提供商

## 贡献

欢迎提交PR和问题到[GitHub仓库](https://github.com/chaosl1996/daily_artwork)

## 许可证

MIT