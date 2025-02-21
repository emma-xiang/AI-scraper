# Toolify.ai 工具爬虫

这是一个用于抓取 [Toolify.ai](https://www.toolify.ai/) 网站上AI工具信息的Python爬虫程序。

## 功能特点

- 自动化浏览器控制，支持无头模式运行
- 智能页面解析，提取工具名称、描述和链接
- 增量式更新，避免重复抓取
- 数据自动去重和备份机制
- 完善的错误处理和重试机制
- 详细的日志记录

## 项目结构

```
toolify-scraper/
├── requirements.txt      # 项目依赖
├── config.py            # 配置文件
├── scraper/
│   ├── __init__.py
│   ├── browser.py       # 浏览器管理
│   ├── parser.py        # 页面解析
│   └── storage.py       # 数据存储
└── main.py              # 主程序入口
```

## 安装说明

1. 克隆仓库
```bash
git clone [repository-url]
cd toolify-scraper
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 确保安装了Chrome浏览器

## 使用方法

1. 运行爬虫程序
```bash
python main.py
```

2. 数据输出
- 抓取的数据将保存在 `data/tools.csv` 文件中
- 每次运行前会自动备份已有数据
- 日志文件保存在 `scraper.log`

## 配置说明

可以在 `config.py` 中修改以下配置：

- 浏览器设置（无头模式、超时时间等）
- 爬虫参数（滚动等待时间、重试次数等）
- 数据存储选项（文件编码、列设置等）
- 日志配置

## 数据格式

抓取的工具信息包含以下字段：

- tool_name: 工具名称
- description: 工具描述
- url: 工具链接
- category: 工具分类
- added_date: 添加日期

## 注意事项

- 请遵守网站的robots.txt规则
- 建议设置适当的请求间隔，避免对目标网站造成压力
- 定期备份数据文件

## License

MIT License