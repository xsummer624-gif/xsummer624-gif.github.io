# ipynb2hugo 使用说明

将 Jupyter Notebook (.ipynb) 一键转换为 Hugo 博客文章。

## 环境要求

- Python 3.x + nbconvert（本机用 miniconda3 的 Python，路径 `C:\Users\53609\miniconda3\python.exe`）
- Hugo（本地预览用）
- 博客项目结构中存在 `content/posts/` 目录

## 快速开始

```bash
cd C:\Users\53609\Desktop\sunny\blog\my-learning-blog
python tools/ipynb2hugo.py "E:/code/Projects/MachineLearning/ch02_base/feature/1_低方差.ipynb" --tags 机器学习,特征工程 --category 机器学习
```

转换完成后本地预览：

```bash
hugo server
```

浏览器打开 `http://localhost:1313/` 查看效果。

## 命令参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `ipynb` | .ipynb 文件路径（必填） | `"E:/code/.../1_低方差.ipynb"` |
| `--tags` | 标签，逗号分隔 | `--tags 机器学习,特征工程` |
| `--category` | 分类 | `--category 机器学习` |
| `--fold` | 输出超过 N 行则折叠（默认 15，设 0 不折叠） | `--fold 10` |
| `--blog-dir` | 博客根目录（默认自动检测） | `--blog-dir D:/blog` |

## 转换流程

1. **nbconvert 转换**：.ipynb → .md + 图片文件夹
2. **添加 front matter**：自动生成 TOML 格式头部（标题、日期、标签、`math = true`）
3. **长输出折叠**：超过 15 行的代码输出自动折叠为可点击展开区域
4. **创建 Page Bundle**：在 `content/posts/<标题>/` 下生成 `index.md` + 图片文件夹

## 标题提取规则

从文件名自动提取，去掉开头的数字前缀：

| 文件名 | 提取标题 |
|--------|---------|
| `1_低方差.ipynb` | 低方差 |
| `03-data-clean.ipynb` | data-clean |
| `特征选择.ipynb` | 特征选择 |

## 注意事项

### 图片路径

nbconvert 生成的图片会放在 `<文件名>_files/` 文件夹中，脚本会自动复制到 Page Bundle 目录内。md 中的引用路径 `![png](xxx_files/yyy.png)` 不需要手动修改，Hugo 会正确解析。

### 数学公式

front matter 自动加上 `math = true`，页面会加载 MathJax。支持：
- 行内公式：`$y = wx + b$`
- 块级公式：`$$\int f(x)dx$$`

### 代码高亮

博客使用自定义配色方案（基于 PyCharm Darcula 调整）：

| 元素 | 颜色 |
|------|------|
| 关键字（import/from/as/def） | 橙棕 `#CC7832` |
| 字符串 | 绿色 `#98C379` |
| 数字 | 亮蓝 `#61AFEF` |
| 注释 | 绿色斜体 `#6A9955` |
| 内建函数（print） | 紫色 `#C586C0` |
| 函数/方法/变量/类名 | 白色 `#D4D4D4` |
| 关键字参数名（括号内的 `name=value`） | 深橙红 `#B5522A` |
| 装饰器 | 黄绿 `#BBB529` |
| 背景 | 深灰 `#2B2B2B` |

### 长输出折叠

代码输出超过 15 行自动折叠，显示为「📎 输出（N 行，点击展开）」。用 `--fold` 调整阈值：

```bash
# 10 行就折叠
python tools/ipynb2hugo.py notebook.ipynb --fold 10

# 不折叠
python tools/ipynb2hugo.py notebook.ipynb --fold 0
```

### Markdown 加粗语法

Hugo 的 Goldmark 渲染器对中文标点紧跟的加粗有 bug。`**文字**：`（冒号紧跟）可能不渲染为加粗。解决方法：用 HTML 标签 `<strong>文字</strong>` 替代。

## 发布流程

1. 转换：`python tools/ipynb2hugo.py notebook.ipynb --tags ...`
2. 本地预览：`hugo server`，检查 `http://localhost:1313/`
3. 如需修改内容，直接编辑 `content/posts/<标题>/index.md`
4. **push 前跑一下标点修复**（防止中文逗号/引号导致部署失败）：

```bash
python tools/fix_frontmatter.py
```

5. 满意后上传：

```bash
git add .
git commit -m "新增文章：标题"
git push
```

GitHub Actions 会自动构建并部署到 `https://xsummer624-gif.github.io/`。

## 标点修复工具 (fix_frontmatter.py)

手动编辑文章标签时容易混入中文标点（逗号 `，`、引号 `""`），导致 TOML 解析失败、部署报错。

**用法：**

```bash
python tools/fix_frontmatter.py
```

**功能：**
- 扫描 `content/posts/` 下所有 .md 文件
- 在 front matter（`+++` 之间）中自动替换：
  - 中文逗号 `，` → 英文逗号 `,`
  - 中文引号 `""` → 英文引号 `""`
  - 中文单引号 `''` → 英文单引号 `''`
- 清理 front matter 内多余空行
- 输出修复报告

**建议：每次 push 前跑一遍，几秒钟搞定，不会再部署失败。**

## 常见问题

**Q: 转换报错 "找不到安装了 nbconvert 的 Python 环境"**

A: 确保用 miniconda3 的 Python 运行脚本：
```bash
C:\Users\53609\miniconda3\python.exe tools/ipynb2hugo.py notebook.ipynb
```

**Q: 图片显示不出来**

A: 确认图片文件夹在 Page Bundle 目录内（`content/posts/<标题>/<文件名>_files/`），且 md 中引用路径是相对路径。

**Q: 同名文章重复转换**

A: 脚本会覆盖同名目录。如需保留旧版本，先修改文件名或手动备份。
