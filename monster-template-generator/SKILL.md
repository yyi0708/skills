---
name: monster-template-generator
description: >
  为"小怪打卡队"App 生成可导入的图鉴/妖兽/怪物模板 ZIP 包。
  当用户提及以下任一概念时必须触发此 skill: 生成图鉴/妖兽/怪物/精灵/宠物/灵兽/异兽模板/小怪打卡队图鉴;
  给小怪打卡队或打卡App创建怪物集合; 为一个主题（动漫、小说、神话、游戏、动物、幻兽）搜资料后打包成 ZIP 图鉴;
  用户说"帮我弄个模板"、"打包一个模板"时若上下文涉及怪物/妖兽/收藏品图鉴也应触发。
  该 skill 执行: 理解用户输入 → 搜索主题数据 → 设计条目 → AI 生成精美图片 → 打包为 App 可直接导入的 ZIP 文件。
---

# 妖兽模板生成器 (Monster Template Generator)

为"小怪打卡队"App 生成可导入的妖兽（怪物/宠物/动漫）模板 ZIP 包。

## 数据格式

### ZIP 目录结构

```
<template-name>.zip
├── template.json           # 模板与妖兽配置 (必需, UTF-8)
└── images/
    ├── cover.png           # 模板封面图 (建议 512×512, PNG)
    ├── monster_1.png       # 每只妖兽对应一张图片
    ├── monster_2.png
    └── ...
```

### template.json

```json
{
  "name": "仙剑奇侠传·妖兽录",
  "description": "取自《仙剑奇侠传》经典设定的妖兽，古风仙侠风格。",
  "version": "1.0.0",
  "cover": "images/cover.png",
  "monsters": [
    {
      "name": "雷灵兽",
      "description": "赵灵儿以雷灵珠之力唤出的上古灵兽，青紫电光缭绕，形似麒麟而带羽翼。",
      "rarity": "elite",
      "category": "雷系·灵兽",
      "image": "images/monster_1.png",
      "sortOrder": 0
    }
  ]
}
```

**字段说明:**

| 字段          | 类型   | 必须 | 说明                               |
| ------------- | ------ | ---- | ---------------------------------- |
| `name`        | string | 是   | 模板名称                           |
| `description` | string | 否   | 模板描述                           |
| `version`     | string | 是   | 语义化版本号, 默认 `1.0.0`         |
| `cover`       | string | 是   | 封面图相对路径, `images/cover.png` |
| `monsters`    | array  | 是   | 妖兽数组                           |

**单个 monster 字段:**

| 字段          | 类型   | 必须 | 说明                                                                    |
| ------------- | ------ | ---- | ----------------------------------------------------------------------- |
| `name`        | string | 是   | 妖兽名称                                                                |
| `description` | string | 否   | 描述                                                                    |
| `rarity`      | string | 是   | `normal` / `elite` / `boss` (也兼容中文: 普通/精英/稀有/史诗/传说/BOSS) |
| `category`    | string | 是   | 分类标签, 如 火系/草系/凶兽/神兽                                        |
| `image`       | string | 是   | 图片相对路径, 如 `images/monster_1.png`                                 |
| `sortOrder`   | int    | 否   | 排序序号                                                                |

**rarity 与数值关系:**

- `normal`: 无加成
- `elite`: baseCoins/baseXp +10
- `boss`: baseCoins/baseXp +15

### 图片要求

- 格式: PNG (推荐) 或 JPG/JPEG
- 尺寸: 至少 256×256，建议 512×512
- 封面 `cover.png` **必须存在**
- 每只妖兽一张独立图片
- **所有图片必须放在 `images/` 子目录中**, 与 `template.json` 同级

## 工作流程

### 第1步: 搭建工作目录

在工作目录下创建以下结构:

```bash
mkdir -p /tmp/monster_template_<随机后缀>/images
```

### 第2步: 理解用户意图

用户的输入可能是: 主题关键词、一段描述、小说/游戏/动漫名称、URL 链接, 或以上混合。如主题模糊, 主动搜索相关信息来丰富内容。

### 第3步: 搜索网络获取数据

- 使用 `websearch` 搜索主题相关的图鉴/怪物/妖兽/角色数据
- 收集名称、特征、分类、出处等信息
- 用户提供了 URL 则用 `webfetch` 获取
- 默认生成 18 只图鉴, 用户有要求则按用户要求

### 第4步: 设计图鉴条目

- 每个条目确定: name / description / rarity / category / sortOrder
- **不要给所有图鉴都设定 high rarity** — normal/elite/boss 应合理分布 (若生成 18 只图鉴，通常 8-10 normal, 6-8 elite, 3-4 boss)
  - 如果主题全是传说级生物(如上古神兽), 允许减少 normal 比例
  - 否则确保有足够的 normal 级别图鉴
- category 根据主题设定
- description 简洁有特色, 不必太长

### 第5步: 判断是否需要生成图片

**如果用户附件了图片文件夹**（提供了已有图片资源）:

- **跳过图片生成步骤**
- 将用户提供的图片复制到工作目录 `images/` 下
- **优先用模型视觉能力识别每张图片** — 自动识别图中怪物/妖兽的特征、类别、稀有度等，简洁准确地填入结构化数据
- 生成一个简易 HTML 页面，列出每张图片与对应妖兽数据的映射关系（图片缩略图 + name/rarity/category/description），便于用户直观预览，对应数据可更改
- 将 HTML 保存到工作目录（如 `preview.html`），告知用户可打开预览确认
- 用户可选择: 打开 HTML 预览并确认，支持 JSON 数据导出，粘贴路径按要求修改或直接输入描述要求修改

**如果没有图片附件**:

- 优先使用当前已加载的图片生成相关 skill 生图 (如 `ai-image-generation`, `openrouter-images` 等)
- 不限制具体 skill，按当前环境可用的工具灵活选择
- 若无可用图片生成工具，推荐安装热门的 (如 `npx skills add openrouterteam/skills@openrouter-images -g -y`) 并告知用户

生成/处理图片时:

- **每张图片都必须通过对应工具写入工作目录的 `images/` 子目录**
- 所有图片风格统一
- 如生成失败, 记下失败的文件名, 继续生成其他图片, **不要中断整个流程**
- 生成完后确认 `images/` 目录下有对应文件

### 第6步: 创建 template.json

在工作目录根目录创建 `template.json`, 严格遵循上述格式:

```bash
cat > "$WORK_DIR/template.json" << 'EOF'
{
  "name": "模板名称",
  "version": "1.0.0",
  "cover": "images/cover.png",
  "monsters": [...]
}
EOF
```

**覆盖所有图片不要遗漏**: monster 中 `image` 字段引用的图片文件必须在 `images/` 中真实存在。

### 第7步: 打包前校验

打包前, 确认工作目录结构完全正确:

```bash
ls -la "$WORK_DIR/"
# 必须看到: template.json  images/
ls -la "$WORK_DIR/images/"
# 必须看到: cover.png  以及每只妖兽的图片
```

**如果缺少 `images/` 目录或图片, 需要从 ZIP 中提取或重新生成。**

### 第8步: 打包为 ZIP

使用 build_zip.py 打包, ZIP 文件名必须使用模板名称:

```bash
ZIP_NAME="<模板名称>.zip"
python3 ~/.agents/skills/monster-template-generator/scripts/build_zip.py "$WORK_DIR" "$ZIP_NAME"
```

### 第9步: 输出结果

告诉用户:

1. ZIP 文件的完整路径 (绝对路径)
2. 包内包含的妖兽列表 (名称 + 稀有度 + 分类)
3. 提示可在 App "图鉴管理 → 导入模板" 中导入使用

## 工作目录示例

打包前的完整目录结构:

```
/tmp/monster_template_a1b2c3/
├── template.json
└── images/
    ├── cover.png
    ├── monster_1.png
    ├── monster_2.png
    └── monster_3.png
```

## 错误处理

- 图片生成部分失败：能生成多少就生成多少，缺失的图片在输出时告知用户
- 搜索无结果：询问用户是否提供更多信息，或基于通用幻想主题生成
- ZIP 打包失败：检查目录结构，确保 `template.json` 和 `images/` 都存在且文件非空
- 任何时候都不要终止流程让用户等待；遇到错误做最佳努力后给出结果并说明情况
