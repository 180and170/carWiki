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

### GitHub Pages 部署（详细步骤）

部署成功后，网站将可通过 `https://180and170.github.io/CarWiki/` 访问。

#### 第一步：合并 PR 到 main 分支

将当前 PR 合并到 `main` 分支。合并后的代码才会触发 GitHub Pages 部署流水线。

#### 第二步：开启 GitHub Pages（仓库 Settings）

1. 打开仓库页面 → 点击顶部菜单栏的 **Settings**（设置）
2. 左侧菜单滚动找到 **Pages**，点击进入
3. 在 **Build and deployment** 区域：
   - **Source** 下拉框选择 **GitHub Actions**（不要选 "Deploy from a branch"）
4. 点击 **Save** 保存

> 这一步告诉 GitHub："我的网站由 Actions 工作流来构建和部署"，而不是从某个分支目录直接读取。

#### 第三步：确认 Actions 权限

1. 仍在 Settings 页面，左侧菜单点击 **Actions** → **General**
2. 滚动到页面底部的 **Workflow permissions**
3. 确保选择了 **Read and write permissions**
4. 勾选 **Allow GitHub Actions to create and approve pull requests**（可选）
5. 点击 **Save** 保存

#### 第四步：触发部署

部署有三种触发方式（任选其一）：

**方式 A：推送到 main 时自动触发**
- 合并 PR 或向 `main` 推送对 `docs/` 或 `data/` 的修改，会自动触发 `deploy.yml` 工作流

**方式 B：手动触发爬虫 + 部署**
1. 打开仓库页面 → 点击顶部的 **Actions** 标签页
2. 左侧列表中找到 **Scrape & Deploy** 工作流
3. 点击右侧的 **Run workflow** 按钮
4. 选择 `main` 分支，点击绿色的 **Run workflow** 确认
5. 等待工作流完成（大约 5-10 分钟），期间会执行爬虫 → 提交数据 → 部署网页

**方式 C：定时自动执行**
- 已配置为每周一 UTC 06:00（北京时间 14:00）自动执行爬虫并部署

#### 第五步：查看部署结果

1. 在 **Actions** 标签页可以看到工作流运行状态（绿色对勾 = 成功）
2. 在 **Settings → Pages** 页面会显示网站 URL：
   - `https://180and170.github.io/CarWiki/`
3. 点击 URL 即可访问网站

#### 常见问题排查

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| Actions 运行失败 | Pages 未设置为 GitHub Actions 模式 | Settings → Pages → Source 改为 GitHub Actions |
| 404 Page not found | 部署尚未完成或未触发 | 检查 Actions 是否有运行中的工作流 |
| 网页显示"数据加载失败" | data 目录未正确复制 | 检查 deploy.yml 中的 `cp -r data docs/data` 步骤日志 |
| 样式/脚本加载不出来 | 路径问题 | 确认仓库名是否为 CarWiki（影响子路径） |

### 手动触发爬虫

在 GitHub 仓库的 Actions 标签页中，选择 `Scrape & Deploy` workflow，点击 `Run workflow` 即可手动触发爬虫更新。爬虫完成后会自动提交新数据到仓库并重新部署网站。

## 技术栈

- **爬虫**: Python 3.12 + Requests + BeautifulSoup4 + lxml
- **前端**: 原生 HTML5 / CSS3 / JavaScript（无框架依赖）
- **部署**: GitHub Pages（静态托管）
- **自动化**: GitHub Actions（定时爬虫 + 自动部署）

## 许可协议

本项目代码采用 MIT 协议。数据来自各品牌官方网站的公开信息，版权归原品牌所有。
