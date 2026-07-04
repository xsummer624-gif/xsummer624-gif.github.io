+++
title = "博客文章编写指南"
date = 2026-07-04
draft = false
tags = ["随笔", "博客"]
categories = ["博客相关"]
summary = "记录这个博客的 md 文件字段格式和作用，方便以后写文章时查阅。"
+++

## 这是什么

这篇文章记录了博客文章的 front matter（文件头部配置）字段格式和作用，方便我以后写文章的时候查阅。

---

## Front Matter 格式

每篇 md 文件最上面要有一段配置，用 `+++` 包裹起来（Hugo 的 TOML 格式），长这样：

```toml
+++
title = "文章标题"
date = 2026-07-04
draft = false
tags = ["标签1", "标签2"]
categories = ["分类"]
summary = "一句话摘要"
+++
```

`+++` 上面不能有空行，下面就是正文。

---

## 所有字段说明

### 必填字段

#### title

文章标题，显示在文章列表和文章详情页。

```toml
title = "Python 装饰器学习笔记"
```

#### date

发布日期，决定文章排序（新的在前）和归档位置。格式是 `YYYY-MM-DD`。

```toml
date = 2026-07-04
```

#### draft

是否为草稿。`true` = 草稿（不会发布到网站），`false` = 正式发布。

```toml
draft = false
```

### 常用字段

#### tags

标签，可以写多个，用逗号分隔。不需要预先定义，写文章时随便加，网站会自动生成标签页。

```toml
tags = ["Python", "笔记", "爬虫"]
```

#### categories

分类，和标签类似，但层级更高，适合做大类划分。也可以不写。

```toml
categories = ["技术"]
```

#### summary

文章摘要，显示在首页文章列表里。不写的话 Hugo 会自动截取正文前几句。

```toml
summary = "今天学了 Python 装饰器，记录一下基本用法和几个实际场景。"
```

### 可选字段

#### description

给搜索引擎看的页面描述，影响 SEO。和 summary 类似但作用于搜索结果。

```toml
description = "Python 装饰器的基本用法、带参数装饰器、类装饰器的完整教程"
```

#### weight

排序权重，数字越小越靠前。一般不用，默认按日期排序。

```toml
weight = 1
```

#### cover

文章封面图，放图片路径。图片放在 `static/` 目录下。

```toml
cover.image = "/images/my-cover.jpg"
```

#### ShowToc

单篇文章是否显示目录，覆盖全局设置。

```toml
ShowToc = true
TocOpen = true
```

---

## 几个完整例子

### 例子一：技术笔记

```toml
+++
title = "Python 装饰器学习笔记"
date = 2026-07-04
draft = false
tags = ["Python", "笔记"]
categories = ["技术"]
summary = "装饰器的基本用法、带参数装饰器、类装饰器。"
+++
```

### 例子二：日常随笔

```toml
+++
title = "七月的第一天"
date = 2026-07-01
draft = false
tags = ["随笔", "生活"]
summary = "随便写写最近的感受。"
+++
```

### 例子三：纯技术记录（最简）

```toml
+++
title = "Git 常用命令"
date = 2026-07-04
draft = false
tags = ["Git"]
+++
```

---

## 正文支持的格式

正文用 Markdown 写，支持以下内容：

**代码块**（带语法高亮）：

```python
def hello():
    print("Hello, World!")
```

**图片**（图片放在 `static/images/` 下，用 `/images/文件名` 引用）：

```markdown
![描述文字](/images/screenshot.png)
```

**引用**：

> 这是一段引用文字

**表格**：

| 命令 | 作用 |
|------|------|
| `git add .` | 暂存所有改动 |
| `git commit -m "msg"` | 提交 |

**列表**：

- 第一项
- 第二项
  - 子项

**粗体和斜体**：

**粗体文字** 和 *斜体文字*

**链接**：

```markdown
[Hugo 官网](https://gohugo.io/)
```

**数学公式**（PaperMod 支持的话）：

```markdown
$$E = mc^2$$
```

---

## 小结

写文章就三件事：

1. 在 `content/posts/` 下新建 `.md` 文件
2. 开头写 front matter（至少写 `title`、`date`、`draft = false`）
3. 下面写正文，Markdown 格式随便发挥

字段记不住没关系，回来翻这篇文章就行。
