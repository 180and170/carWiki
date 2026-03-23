# CarWiki - 1/64 合金车模百科

收录国内外主流 1/64 比例合金车模品牌的产品数据，通过自动化爬虫采集并在网页中展示。

## 收录品牌

| 品牌 | 国家/地区 | 官网 | 特色 |
|------|----------|------|------|
| **Mini GT** | 中国香港 | minigt.com | 超跑、赛车、经典车型 |
| **Tarmac Works** | 中国香港 | tarmacworks.com | 赛车涂装、改装文化 |
| **INNO64** | 中国香港 | inno-models.com | 日系经典、可开门设计 |
| **Era Car** | 中国香港 | eramyth.com | 城市服务车、可开启部件 |
| **Hot Wheels** | 美国 | hotwheels.com | 全球最知名、幻想车型 |
| **Matchbox** | 英国/美国 | matchbox.com | 真实还原、环保系列 |
| **Tomica** | 日本 | takaratomy.co.jp | 日系车型、Limited Vintage |
| **Johnny Lightning** | 美国 | johnny-lightning.com | 美系肌肉车、经典老车 |
| **Majorette** | 法国/泰国 | majorette.com | 欧洲车型、高性价比 |
| **SIKU** | 德国 | siku.de | 工程车辆、农业机械 |
| **KAIDO HOUSE** | 美国/中国香港 | kaidohouse.com | 改装文化、联名Mini GT |
| **Pop Race** | 中国香港 | poprace.com | 流行文化跨界 |
| **GreenLight** | 美国 | greenlighttoys.com | 影视授权、Chase限量版 |

## 项目结构

```
CarWiki/
├── scraper/              # Python 爬虫
│   ├── config.py         # 品牌配置与爬虫设置
│   ├── utils.py          # 通用工具函数
│   ├── run.py            # 爬虫主入口
│   └── brands/           # 各品牌爬虫模块
│       ├── mini_gt.py
│       ├── tarmac_works.py
│       ├── inno64.py
│       ├── tomica.py
│       ├── hot_wheels.py
│       ├── greenlight.py
│       └── generic.py
├── data/                 # 爬虫数据（JSON）
│   ├── catalog.json      # 完整数据集
│   ├── brands.json       # 品牌信息
│   └── products_*.json   # 各品牌产品数据
├── docs/                 # 前端页面（GitHub Pages）
│   ├── index.html
│   ├── style.css
│   └── app.js
├── .github/workflows/    # GitHub Actions
│   ├── scrape.yml        # 定时爬虫 + 部署
│   └── deploy.yml        # 推送时自动部署
└── requirements.txt      # Python 依赖
```

## 使用方式

### 本地运行爬虫

```bash
pip install -r requirements.txt
python3 -m scraper.run
```

### 本地预览网页

```bash
# 将数据复制到 docs 目录
cp -r data docs/data

# 启动本地服务器
cd docs && python3 -m http.server 8000
```

浏览器访问 `http://localhost:8000`

### GitHub Pages 部署

1. 在仓库 Settings → Pages 中设置 Source 为 **GitHub Actions**
2. 推送代码到 `main` 分支，将自动触发部署
3. 也可以手动触发 `Scrape & Deploy` workflow 来更新数据

### 手动触发爬虫

在 GitHub 仓库的 Actions 标签页中，选择 `Scrape & Deploy` workflow，点击 `Run workflow` 即可手动触发爬虫更新。

## 技术栈

- **爬虫**: Python 3.12 + Requests + BeautifulSoup4 + lxml
- **前端**: 原生 HTML5 / CSS3 / JavaScript（无框架依赖）
- **部署**: GitHub Pages（静态托管）
- **自动化**: GitHub Actions（定时爬虫 + 自动部署）

## 许可协议

本项目代码采用 MIT 协议。数据来自各品牌官方网站的公开信息，版权归原品牌所有。
