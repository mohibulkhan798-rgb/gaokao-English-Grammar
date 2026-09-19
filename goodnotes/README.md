# 高三英语课堂进度 · GoodNotes 模版

A4 横向手账，用来记录高三每节英语课的进度。

## 课堂结构

每节课固定两栏：

1. **单词默写**：错词汇总表（正确拼写 / 错误写法 / 词义 / 订正 / 会了）
2. **语法**：留白手写今日语法点、规则和例句

剩下的课时按阅读、写作交替：

| 课次 | 课型 |
| --- | --- |
| 第 1 节 | 开课建档 |
| 第 2 节 | 阅读 |
| 第 3 节 | 写作 |
| 第 4 节 | 阅读 |
| 之后 | 继续交替 |

## 文件

| 文件 | 用途 |
| --- | --- |
| [高三英语课堂进度手账.pdf](./高三英语课堂进度手账.pdf) | 完整 25 页笔记本（封面、说明、学期总览、20 节编号课页、阅读/写作空白加页） |
| [templates/阅读课.pdf](./templates/阅读课.pdf) | 单页模版，可加入 GoodNotes 模板库后重复加页 |
| [templates/写作课.pdf](./templates/写作课.pdf) | 单页模版 |
| [templates/开课第1节.pdf](./templates/开课第1节.pdf) | 第 1 节开课建档页 |
| [templates/学期总览.pdf](./templates/学期总览.pdf) | 学期进度总表 |
| [class-log.html](./class-log.html) | 浏览器预览源文件 |
| `build.py` | 重新导出 PDF |

## 导入 GoodNotes

**推荐：整本导入**

1. 把 `高三英语课堂进度手账.pdf` 发到 iPad（隔空投送 / iCloud / 文件 App）
2. 用 GoodNotes 打开，选「导入为新文档」
3. 纸张比例保持 A4 横向，用 Apple Pencil 直接在表格和横线上填写

**若要放进模板库、随时加页**

GoodNotes 的模板库对多页 PDF **只收第一页**，所以请分别导入 `templates/` 里的单页文件：

1. GoodNotes 文档库 → 右上角设置 → Notebook Templates
2. Paper 尺寸选 **A4 · Landscape**（不要选 GoodNotes Standard）
3. 新建分组「高三英语」，分别导入阅读课、写作课、开课第 1 节、学期总览

## 重新生成

```bash
python3 goodnotes/build.py
```

需要本机已安装 Google Chrome 与 Noto CJK 字体。
