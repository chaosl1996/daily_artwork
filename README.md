# 每日名画 (Daily Artwork) 集成

Home Assistant集成，用于每日获取世界名画信息并在界面中展示。

## 功能特点
- 每3小时自动从API获取一幅名画信息
- 显示作品名称、作者、图片和简介
## 安装方法
  1. 将此目录复制到Home Assistant的`custom_components`文件夹中

## 配置方法
在`configuration.yaml`中添加以下配置：
```yaml
sensor:
  - platform: daily_artwork
```
2. 重启Home Assistant
3. 在集成页面搜索并添加"每日名画"

## 配置选项
- 更新间隔: 数据刷新频率（秒），默认3小时(10800秒)

## 使用方法
添加集成后，将自动创建:
- 名为"名画"的传感器实体

## 实体属性
传感器包含以下属性:
- `image`: 作品图片URL
- `author`: 作者名称
- `text`: 作品简介（前四行）

## 故障排除
- 确保网络连接正常
- 检查API是否可访问
- 查看Home Assistant日志获取详细错误信息

## 可能的改进
- 添加更多作品信息展示
- 支持多语言切换
- 实现图片缓存
