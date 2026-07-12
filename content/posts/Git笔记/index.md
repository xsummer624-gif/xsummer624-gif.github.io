+++

title = "Git"
date = 2026-07-12
draft = false
tags = ["Git","笔记"]
summary = "Git 的思想、原理与核心命令——为什么这样设计，怎么用，以及底层的统一模型"

++++

# Git

## 一、核心思想：Git 是"对象 + 指针"

Git 是一个分布式版本控制系统。抛开所有命令不谈，它底层只做两件事：

1. **存对象**：把每次提交的项目快照按内容哈希存进 `.git/objects/`
2. **移指针**：分支、HEAD、tag 都是小文件，里面写着一个 commit 的哈希

所有 Git 命令——commit、branch、merge、reset、checkout——本质上都是**"读写对象 + 移动指针"**。理解这一点，后面所有操作都不用背。

Linus 在 2005 年仅用 10 天写出 Git 原型，这个原型能沿用 20 年几乎不改设计，靠的不是功能多，而是三个底层设计决定的直觉：

- **快照而非增量**：每次 commit 存完整项目状态，不是"改了什么"
- **内容寻址存储**：对象用内容的 SHA-1 哈希做唯一标识，相同内容天然去重
- **分布式对等**：每个克隆都是完整仓库，本地和远程结构一样

这三个决定，决定了 Git 的速度、离线能力、分支轻量、回滚容易。下面展开。

---

## 二、快照与对象模型：Git 的根基

### 为什么要存快照而不是增量

传统 VCS（CVS/SVN、数据库的 redo log）存的是"做了什么操作"——追加了几行、删了哪段。要取某个历史版本，得从初始状态回放所有 delta 才能算出来，越早的版本越慢。

Git 反过来：**每次 commit 存"现在长什么样"的完整快照**。要取任意历史版本，直接读那个 commit 的快照即可，O(1)。

代价是占空间——但 Git 用去重 + 压缩把代价压下去，换来速度、离线、简单。这是典型的"空间换时间"取舍，在现代磁盘下非常划算。

### 四大对象

Git 底层只有四种对象，都存在 `.git/objects/`，用 SHA-1 哈希做唯一标识：

| 对象 | 存什么 | 关键点 |
|------|--------|--------|
| **blob** | 单个文件的完整内容 | 不含文件名、不含路径 |
| **tree** | 一个目录的结构 | 记录"文件名 → blob 哈希"、"子目录名 → 子 tree" |
| **commit** | 一次快照 | 指向顶层 tree + 父 commit + 作者/时间/消息 |
| **tag** | 带注释的标签 | 指向某 commit + 标签说明（annotated tag） |

引用关系：

```
        ┌──────────┐
        │  commit  │  快照 + 父提交 + 元信息
        └────┬─────┘
             │ 指向
             ▼
        ┌──────────┐
        │   tree   │  顶层目录
        └────┬─────┘
             │ 递归引用
      ┌──────┴──────┐
      ▼             ▼
  ┌────────┐   ┌──────────┐
  │  blob   │   │ sub-tree │
  └────────┘   └──────────┘
```

### 快照的存储逻辑（关键）

- 改了某个文件 → 为它新建一个 blob，存完整新内容
- **没改的文件 → tree 里直接填旧 blob 的哈希，那个 blob 一动不动、不重新存**

所以一个 commit 引用很多 blob，其中新 blob 是本次新增的，旧 blob 是复用以前就存在的。整个仓库里所有 blob 永远只存一份（按内容哈希去重）。

> **核心区别**：redo log 存"做了什么操作"，Git 存"现在长什么样"。Git 是状态快照，不是操作日志。

### 深度思考：逻辑完整 + 物理增量

这是 Git 最优雅的地方：

- **逻辑上**是完整快照——每个 commit 都代表那一刻整个项目的完整状态，简单直观
- **物理上**是增量去重——只有改动的文件产生新 blob，没改的全复用

两层结合，既得到了"取任意版本 O(1)"的速度，又避免了"每次存全量"的空间浪费。靠的就是**内容寻址存储**——内容决定哈希，哈希决定身份，相同内容在数学上就是同一份存储。

磁盘占用再靠两层优化缓解：
1. **packfile 压缩**：`git gc` 把松散对象打包成 `.pack`，用 zlib 压缩 + delta 压缩（同文件多版本只存差异）
2. **partial clone**：新版 Git 支持按需拉取 blob，不一次下全历史

---

## 三、三区模型与基本命令

### 三个区的数据流

```
┌──────────────┐   git add    ┌──────────────┐  git commit  ┌──────────────┐
│  工作区       │ ────────────▶│   暂存区      │ ───────────▶│  本地仓库    │
│ Working Dir  │              │   Index      │             │  .git/objects│
│              │◀─────────────│              │◀───────────│             │
└──────────────┘ git checkout └──────────────┘ git reset   └──────────────┘
   你编辑的文件               "下次提交清单"              commit 历史链
```

### 为什么要暂存区（思想）

很多人觉得暂存区多此一举——为什么不直接从工作区 commit 到仓库？

因为**暂存区让你精确控制一次 commit 的粒度**。你改了 5 个文件，可能只其中 3 个属于"修复登录 bug"，另外 2 个属于"加新功能"。暂存区就是个"购物车"，让你分批把改动组织成有意义的 commit，而不是"把当前所有改动一股脑提交"。

没有暂存区，你的 commit 历史会变成"乱七八糟一大堆改动"，没法回滚、没法 review、没法写有意义的提交信息。

### 基本命令语法

```bash
# 初始化本地仓库（在项目目录下执行，生成 .git/ 隐藏目录）
git init

# 设置签名（区分操作者身份，每次提交都会带上）
git config --global user.name "用户名"        # 全局，写入 ~/.gitconfig
git config --global user.email "邮箱"
git config user.name "用户名"                  # 仅当前仓库，写入 .git/config（优先级更高）

# 查看状态
git status                                     # 看工作区/暂存区有什么变动
git status -s                                  # 精简版

# 加入暂存区
git add 文件名                                  # 单个文件
git add .                                      # 当前目录所有改动（含新增/修改）
git add -A                                     # 整个仓库所有改动

# 提交到本地仓库
git commit -m "提交说明"                        # 提交暂存区内容
git commit 文件名 -m "说明"                     # 只提交指定文件（会自动 add）
git commit --amend                             # 修改最近一次 commit（追加改动 + 改消息）

# 查看历史
git log                                        # 完整历史（哈希、作者、日期、消息）
git log --oneline                              # 精简（短哈希 + 消息，一行一个）
git log --oneline -10                          # 最近 10 条
git log --graph --oneline --all                # 带分支图（看分叉/合并最直观）
git reflog                                     # 指针移动记录（含已"删除"的提交，找回用）

# 对比差异
git diff                                       # 工作区 vs 暂存区
git diff --cached                              # 暂存区 vs 最近 commit
git diff HEAD                                  # 工作区 vs 最近 commit
git diff <commit1> <commit2>                   # 两个 commit 之间

# 撤销改动
git checkout -- 文件名                          # 撤销工作区的改动（用暂存区覆盖）
git restore 文件名                              # 同上（新语法，更清晰）
git rm 文件名 && git commit -m "删除"           # 删除文件并提交
```

### 一次 commit 内部发生了什么

把命令和对象模型串起来：

1. 你在工作区改了 `a.txt`
2. `git add a.txt` → Git 计算 a.txt 新内容的哈希，存成新 blob，在 index 里更新"a.txt → 新哈希"
3. `git commit -m "fix"`：
   - 用 index 当前内容生成新 tree（顶层目录快照，引用新 blob + 复用旧 blob）
   - 生成新 commit 对象（父 = HEAD 指向的 commit，tree = 刚生成的 tree）
   - 把当前分支指针从旧 commit 移到新 commit
   - 记一条 reflog

所以一个 commit 真正"新增"的存储 = 改动文件的完整新内容 + 一棵新 tree + 一个 commit 对象。没改的文件零开销。

---

## 四、分支：Git 的灵魂

### 分支只是 41 字节的指针（思想）

这是 Git 最反直觉、也最精妙的设计。

很多人以为"开分支 = 复制一份代码"，**完全不是**。分支在 Git 里就是 `.git/refs/heads/` 下一个小文件，里面装一个 40 字符的 commit 哈希：

```
.git/refs/heads/main    内容: abc123...   ← main 指向 commit abc123
.git/refs/heads/dev     内容: def456...   ← dev  指向 commit def456
```

创建分支 = 新建一个 41 字节的文件，不复制任何代码，瞬间完成（O(1)）。对比 SVN 创建分支要复制整个目录（O(项目大小)），这就是 Linus 说"分支很便宜，随便开"的原因。

### HEAD 是另一个指针

`.git/HEAD` 文件内容是 `ref: refs/heads/main`，意思是"我现在在 main 分支上"。切换分支就是改这一行字。

| 概念 | 本质 | 会移动吗 |
|------|------|---------|
| **commit** | 快照对象 | 不动（哈希固定） |
| **分支** | 指向某 commit 的指针 | 会（随 commit 前移） |
| **HEAD** | 指向当前分支的指针 | 会（随 checkout 切换） |
| **tag** | 指向某 commit 的指针 | 不动（固定标签） |

### 分叉何时发生（深度思考）

分支刚创建时，两个指针指向同一个 commit，没区别。真正的"分叉"发生在**你在分支上做新 commit 那一刻**，不是 `checkout -b` 那一刻：

```
commit-1 ← commit-2 ← commit-3
                                ├─ main:  commit-3 → commit-6 → commit-7
                                └─ dev:   commit-3 → commit-4 → commit-5
```

- commit-1、2、3 是两个分支**共享**的，没有复制，就一份
- 从 commit-3 往后，两条线各自新增自己的 commit

**分支不是"从主线复制出来的"，而是"和主线共享同一个历史起点，从某个 commit 开始往后各自生长"**。`checkout -b` 只是给你一个"未来可以分叉的起点指针"，分叉的实际成本发生在 commit 那一刻，而且只产生被改文件的新 blob。

### 分支命令语法

```bash
git branch -v                                  # 查看所有本地分支（-v 带最后 commit 信息）
git branch 分支名                               # 创建分支（不切换）
git checkout 分支名                             # 切换分支（移动 HEAD）
git checkout -b 分支名                          # 创建并切换（最常用）
git switch 分支名                               # 新语法，只切换（比 checkout 语义清晰）
git switch -c 分支名                            # 新语法，创建并切换
git branch -d 分支名                            # 删除分支（已合并才能删）
git branch -D 分支名                            # 强制删除
git merge 分支名                                # 把指定分支合并到当前分支
```

### 合并的两种情况

**情况 A：fast-forward（快进合并）**
当前分支没有新提交，被合并分支有，直接把当前分支指针前移到对方位置，不产生新 commit：

```
之前: main → commit-3    dev → commit-5
之后: main → commit-5    dev → commit-5    （main 指针前移）
```

**情况 B：真合并（产生 merge commit）**
两边都有新提交，Git 创建一个新 commit，它有**两个父提交**，把两条线的改动合到一起：

```
commit-3 ← commit-6 ←─┐
          │           ← merge-commit-7
          └ commit-5 ←┘
```

### 深度思考：分支和回滚本质统一

分支和回滚看起来是两回事，底层却是同一件事的两种用法：

| 操作 | 改了什么 | 动 blob 吗 |
|------|---------|-----------|
| 切分支 `git checkout dev` | HEAD 指向 dev | 不动，工作区换内容 |
| 回滚 `git reset --hard <commit>` | 当前分支指针指向旧 commit | 不动，工作区换内容 |

都是"改指针 + 工作区读出对应快照"。区别只是：
- **回滚** = 当前分支指针本身往后退（同一条线上纵向后退，放弃新东西）
- **分支** = 新建指针从某 commit 另起一条线（在不同指针间横向切换，保留旧东西）

所以可以把分支理解成"一个有名字的、能独立往前走的回滚点"。tag 则是"固定不动的回滚点"。Git 里所有"导航"概念，本质都是指向某个 commit 的指针，只是移动规则不同。

---

## 五、回滚与撤销

### 回滚的本质（思想）

回滚不是"删除新东西"，而是**把指针挪回旧 commit，复用早就存好的旧 blob**。不新增任何存储，不删任何 blob。

旧 commit 在回滚后没人引用了，但它的 blob 还在磁盘里——通过 `git reflog` 能找到那个哈希，`git reset --hard <那个哈希>` 就能瞬间回去。这就是 Git 圈那句话："**Git 里几乎没有真正的删除，只要 commit 过就能找回**。"

### 三种 reset 模式（关键区别）

`git reset` 有三种模式，区别是"指针退回的同时，改动保留到哪一层"：

```bash
git reset --soft <commit>     # 指针退回，改动留在【暂存区】（相当于撤销 commit 但保留 staged）
git reset --mixed <commit>    # 指针退回，改动留在【工作区】（默认行为）
git reset --hard <commit>     # 指针退回，工作区/暂存区全清空（彻底丢弃改动）
```

记忆方式：soft → mixed → hard，**改动保留的位置离 commit 越来越远，丢得越来越彻底**。

### reset vs revert（关键区别）

```bash
git reset --hard <commit>      # 改写历史：指针退回，旧 commit 变悬空
git revert <commit>            # 不改历史：新建一个反向 commit，把目标 commit 的改动反过来做一遍
```

**为什么有两种？** 因为历史是"公共财产"：

- `reset` 改写历史，如果那个 commit 已经 push 到远程、别人可能拉过了，你再 reset 会让他们的历史和你冲突——**只能用于本地未 push 的提交**
- `revert` 不动旧历史，只往前加一个"反向操作"的 commit，历史一直往前增长，别人的历史不会断——**已 push 的公共分支必须用这个**

### 其他撤销操作

```bash
git checkout -- 文件名          # 撤销工作区改动（用暂存区版本覆盖）
git restore 文件名              # 同上（新语法）
git restore --staged 文件名      # 把暂存区的改动撤回工作区（撤销 add）
git commit --amend             # 修改最近一次 commit（追加改动 / 改消息）
```

### reflog：后悔药

```bash
git reflog                    # 查看指针移动历史（含 reset 之前的 commit）
git reset --hard <reflog 中的哈希>   # 回到那个状态
```

reflog 记录所有指针移动，即使是 `reset --hard` 丢弃的 commit 也能从这里找回。Git 对象真正被删除要满足两个条件：变成不可达对象 + 执行 `git gc`。在此之前，都还在。

### 深度思考：为什么有三种 reset

因为"撤销"这件事的语义不止一种：你可能想"撤销提交但保留代码继续改"（soft），可能想"撤销提交和暂存、重新组织"（mixed），也可能想"彻底丢弃、回到过去某个干净状态"（hard）。Git 把这三种语义分开，而不是用一个命令加一堆参数，这是 Unix 哲学——每个工具做好一件事。

---

## 六、rebase：重写历史

### rebase 是什么（思想）

`rebase` = re + base，意思是"换基底"。它的本质是：**把一串 commit 拔起来，接到另一个 commit 上**。

假设你有：
```
commit-1 ← commit-2 ← commit-3
                                ├─ main:  commit-3 → commit-6
                                └─ dev:   commit-3 → commit-4 → commit-5
```

`git checkout dev; git rebase main` 做的事：把 dev 上的 commit-4、commit-5 拿下来，基于 commit-6 重新应用一遍，生成新的 commit-4'、commit-5'：

```
commit-1 ← commit-2 ← commit-3 ← commit-6 ← commit-4' ← commit-5'
                                              ↑                  ↑
                                             main               dev
```

注意：commit-4'、commit-5' 是**新对象**（哈希变了，因为父提交变了），原来的 commit-4、commit-5 变成悬空对象（reflog 还能找回）。dev 分支的历史变成了一条直线，没有分叉。

### rebase vs merge：什么时候用哪个

| | merge | rebase |
|--|-------|--------|
| 历史 | 保留真实的分叉和合并记录 | 改写成一条直线，看不到曾经分叉 |
| 结果 commit | 多一个 merge commit | 没有 merge commit，历史更干净 |
| 安全性 | 不改写历史，已 push 也安全 | 改写历史，已 push 会出事 |
| 适用 | 公共分支、要保留协作痕迹 | 个人分支、整理后再合并 |

**经验法则**：
- 合并到公共分支（main）用 `merge`——保留历史，不改别人的 commit
- 整理自己的功能分支用 `rebase`——把零碎 commit 变干净，或同步主干最新改动
- `git pull` 默认是 fetch + merge，会产生 merge commit；用 `git pull --rebase` 改成 fetch + rebase，历史更线性

### 交互式 rebase：整理历史的利器

```bash
git rebase -i <commit>            # 从指定 commit 之后开始整理（列出这些 commit 让你操作）
git rebase -i HEAD~3              # 整理最近 3 个 commit
```

会打开编辑器列出：
```
pick   abc123  第一次提交
pick   def456  修了个 typo
pick   ghi789  完成功能
```

每个 commit 前的 `pick` 可以改成：
- `pick`：保留
- `reword`：保留，但改提交信息
- `squash`：合并到上一个 commit（把零碎改动并成一个）
- `fixup`：同 squash，但丢弃这个 commit 的提交信息
- `drop`：删除这个 commit

最常见用途：**把"修 typo""修 bug""再修一次"这种零碎 commit squash 成一个干净的 commit**，再合并到主干。

### rebase 冲突

rebase 重新应用每个 commit 时也可能冲突，和 merge 冲突标记一样：
```
<<<<<<< HEAD
...
=======
...
>>>>>>> commit-4
```

解决方式：
```bash
# 1. 编辑冲突文件，删标记
# 2. git add 冲突文件
# 3. 继续 rebase（不是 commit！）
git rebase --continue
# 反悔放弃：
git rebase --abort
# 跳过当前 commit：
git rebase --skip
```

注意：rebase 冲突解决后用 `git rebase --continue`，不是 `git commit`——因为它在"重放"过程中，不是新提交。

### 黄金法则（深度思考）

> **永远不要 rebase 已经 push 到公共分支的 commit。**

因为 rebase 会生成新 commit（哈希变了），如果你 rebase 了别人已经拉过的 commit 再 push，别人的历史和你的就对不上了，再 pull 会产生混乱的冲突。

简单记忆：**rebase 只用在本地还没 push 的 commit，或者只你自己用的私有分支**。一旦 push 到共享分支，就当成"历史已定稿"，之后只能用 revert 不用 rebase。

### 深度思考：rebase 是"改写历史"的哲学

merge 尊重历史——发生过就保留，哪怕是分叉。rebase 认为"历史是可以改写的草稿"——只要还没公开，整理得越干净越好。

这两种哲学对应两种工作流：
- **merge 派**：历史是事实记录，分叉和合并都是真实发生的，保留有助于追查问题
- **rebase 派**：历史是叙述，应该让人读得懂，零碎 commit 应该整理成有意义的步骤

实际项目通常是混合：个人分支用 rebase 整理，合到主干用 merge 保留节点。没有对错，看团队偏好。

---

## 七、远程协作

### 本地和 GitHub 是对等副本（思想）

很多人以为"本地存一种、GitHub 存另一种"，**完全不是**。

`git clone` 会把远程仓库的**所有 blob、tree、commit** 全部下载到本地 `.git/objects/`。本地仓库和远程仓库结构完全一样，都是完整的：

```
你的电脑                              GitHub 服务器
.git/objects/                        服务器仓库
  ├─ blob-111 (a.txt v1)              ├─ blob-111 (a.txt v1)
  ├─ blob-222 (a.txt v2)              ├─ blob-222 (a.txt v2)
  ├─ commit-abc                       ├─ commit-abc
  └─ ... 全部历史                     └─ ... 全部历史
```

两边存的东西一模一样，只是各自的"当前指针位置"可能不同。即使 GitHub 挂了，你本地依然完整可用，所有历史、所有版本、所有分支都在。

### 为什么还需要 GitHub（深度思考）

本地仓库已经完整，那 GitHub 的价值在哪？**不是"存储"，而是"协作中转站"**：

| 需求 | 本地做不到 | GitHub 解决 |
|------|-----------|-------------|
| 多人协作 | 你电脑里的 commit 怎么发给同事 | 提供大家都连得上的中心节点 |
| 备份 | 电脑坏了本地没了 | 远程有副本 |
| 分享/开源 | 让全世界看到 | 托管 + 社交平台 |
| PR/Issue/CI | 纯 Git 没有 | 平台附加功能 |

可以用 GitLab、Gitee、自建服务器替代——**Git 本身不依赖任何远程平台**。远程仓库只是"另一个克隆"，充当稳定的交换中心。

### 远程命令语法

```bash
# 查看远程
git remote -v                                  # 查看所有远程别名和地址
git remote add 别名 远程地址                     # 添加远程仓库别名（常用 origin）
git remote remove 别名                          # 删除远程关联

# 推送（本地 → 远程）
git push 别名 分支名                             # 把本地分支推到远程
git push -u 别名 分支名                          # 首次推送并建立跟踪关系（之后可直接 git push）

# 拉取（远程 → 本地）
git fetch 别名                                  # 把远程新对象拉到本地，但不合并，不改动工作区
git pull 别名 分支名                             # = fetch + merge，拉下来并合并到当前分支
git pull --rebase                              # = fetch + rebase（保持线性历史）

# 克隆（第一次获取）
git clone 远程地址                              # 完整克隆到本地（含全部历史）
git clone 远程地址 目录名                        # 克隆到指定目录
```

### push 和 fetch 到底传了什么

不是传"整个仓库"，而是传**差异对象**：

- `git push`：本地多出来的 commit/tree/blob 复制一份发给远程，远程存进去，把它的分支指针前移
- `git fetch`：远程多出来的对象拉到本地存起来，更新远程跟踪分支（`refs/remotes/origin/main`），不动你的工作区

传输的是"对方没有、本地有"的对象，传完之后两边又各自完整。`git pull = git fetch + git merge`，拉下来顺便合并。

### 深度思考：fetch 和 pull 的设计

`git pull` 看起来方便，但它把"获取"和"合并"两件事捆在一起，出问题时你不知道是 fetch 失败还是 merge 冲突。`git fetch` 分离这两步——先拉下来看看远程有什么，再决定怎么合并。**熟练之后应该用 fetch + merge，不用 pull**，这给你在合并前审查远程改动的机会。

---

## 八、冲突解决

### 为什么会冲突（思想）

合并时，如果两个分支**对同一文件的同一位置**做了不同的修改，Git 没法替你决定用哪个——它只是个工具，不知道你的业务意图。于是它把两套改动都写进文件，用特殊标记隔开，让你人工决定。

如果两个分支改的是不同文件，或同一文件的不同位置，Git 会自动合并，不产生冲突。

### 冲突的表现

合并时状态变成 `MERGING`，冲突文件里会出现：

```
<<<<<<< HEAD
当前分支的代码
=======
被合并分支的代码
>>>>>>> dev
```

### 解决三步骤

```bash
# 1. 编辑冲突文件：删除 <<<<<<<、=======、>>>>>>> 标记，保留你要的代码
# 2. 加入暂存区
git add 冲突文件
# 3. 提交（注意：解决冲突可能涉及多个文件，不能带文件名）
git commit -m "解决冲突"
```

提交后 `MERGING` 状态消失，恢复正常。如果反悔不想合并了：

```bash
git merge --abort                               # 放弃合并，回到合并前状态
```

### 协作纪律（避免冲突的实践）

冲突本质是"多人同时改同一处代码"。避免方式不是技术，是习惯：

- **先 pull 再改**：改之前拉最新代码，避免基于旧版本开发
- **及时 commit/push**：别攒一大堆改动再提交，小步快跑
- **不改同人代码**：各自维护各自模块，公共文件由一人统一维护
- **下班前提交**：别留未提交的改动过夜，第二天别人可能已经改了同一处
- **上班第一件事 pull**：同步昨晚别人的改动

### 深度思考：冲突是协作问题不是技术问题

Git 的冲突解决工具再好用，也只是"事后补救"。真正避免冲突靠的是**分支策略 + 团队规范**——让每个人负责清晰的模块，减少改同一处代码的概率。这是为什么有 Git Flow、GitHub Flow 这些分支模型：用流程约束人的行为，而不是靠工具兜底。

---

## 九、.git 目录结构：把抽象落地到文件

前面所有概念（快照、分支、HEAD、暂存区、reflog）都不是抽象的——它们都是 `.git/` 目录下的具体文件。看完这个目录，Git 就没有黑盒了：

```
.git/
├── HEAD                 # 一个文件，内容是 "ref: refs/heads/main"（指向当前分支）
├── config               # 本仓库配置（用户名、远程地址等）
├── refs/                # 所有"指针"的存放处
│   ├── heads/           #   本地分支：每个分支一个文件，内容是该分支指向的 commit 哈希
│   ├── remotes/         #   远程跟踪分支：如 origin/main，记录上次 fetch 时远程在哪
│   └── tags/            #   标签指针
├── objects/             # 所有对象存储（blob/tree/commit/tag）
│   ├── pack/            #   打包压缩后的对象（节省空间）
│   └── xx/...           #   松散对象（按 SHA-1 前两位分目录，如 1a/2b3c...）
├── index                # 暂存区（二进制文件，记录"下次 commit 包含哪些文件的哪个版本"）
├── logs/                # reflog（指针移动的历史）
│   └── HEAD             #   HEAD 的移动记录，找回"丢失"提交用
└── hooks/               # 钩子脚本（pre-commit、post-merge 等触发点）
```

### 深度思考：每个概念都有物理对应

- 你说"分支 main"？就是 `refs/heads/main` 这个文件，里面 40 个字符
- 你说"HEAD"？就是 `.git/HEAD` 这个文件，一行字
- 你说"暂存区"？就是 `.git/index` 这个二进制文件
- 你说"快照"？就是 `.git/objects/` 下那些按哈希命名的文件
- 你说"reflog"？就是 `.git/logs/HEAD` 这个文本文件

**Git 没有黑盒，没有数据库，没有服务进程**。所有状态都是文件，所有操作都是读写文件。这是 Unix 哲学的极致体现——把复杂系统做成文件系统的子集，可观察、可调试、可脚本化。

---

## 十、常用场景速查

以"遇到什么问题"组织，而不是"有什么命令"。这才是日常真正查的东西。

### 撤销类

**撤销最近一次 commit，但保留改动继续改：**
```bash
git reset --soft HEAD~1      # 改动留在暂存区，可继续 commit
```

**撤销最近一次 commit 和暂存，改动退回工作区：**
```bash
git reset --mixed HEAD~1     # 默认行为，等同于 git reset HEAD~1
```

**彻底丢弃最近一次 commit（连同改动）：**
```bash
git reset --hard HEAD~1
```

**撤销已经 push 的提交（公共分支）：**
```bash
git revert <commit>           # 生成反向 commit，历史不丢，安全 push
git push
```

**修改最近一次 commit 的提交信息：**
```bash
git commit --amend            # 如果没改动文件，只改消息
git push --force-with-lease   # 如果已 push 过，需要强推（见下方强推说明）
```

**把最近 3 个 commit 合并成 1 个：**
```bash
git rebase -i HEAD~3          # 把后两个改成 squash
```

**误删了 commit，想找回：**
```bash
git reflog                    # 找到那个 commit 的哈希
git reset --hard <哈希>        # 回到那个状态
```

### 分支类

**提交到了错误的分支：**
```bash
git log --oneline            # 确认最新 commit 哈希
git reset --hard HEAD~1      # 在错误分支上撤销这个 commit（改动退到工作区用 --mixed）
git checkout 正确分支
git cherry-pick <刚才那个哈希>   # 把那个 commit 摘到正确分支
```

**把某个 commit 单独拿到当前分支：**
```bash
git cherry-pick <commit>     # 摘一个；可多个：git cherry-pick A B C
```

**删除远程分支：**
```bash
git push origin --delete 分支名
```

**本地分支重命名并同步到远程：**
```bash
git branch -m 旧名 新名
git push origin :旧名 新名       # 删旧推新
git push -u origin 新名
```

**开发到一半要切分支处理紧急 bug：**
```bash
git stash                     # 暂存当前未提交的改动（工作区变干净）
git checkout -b hotfix
# 修 bug、commit、合并回主干
git checkout 原分支
git stash pop                  # 恢复之前暂存的改动
```

**stash 进阶：**
```bash
git stash list                # 查看所有暂存
git stash apply               # 恢复但不删除 stash
git stash pop                 # 恢复并删除 stash
git stash drop                # 删除一个 stash
```

### 同步类

**把远程最新改动合到本地，保持线性历史：**
```bash
git pull --rebase             # fetch + rebase，不会产生 merge commit
```

**只看远程有什么，不合并：**
```bash
git fetch
git log HEAD..origin/main     # 看远程比本地多了哪些 commit
git merge origin/main         # 决定合并了再合
```

**本地落后远程，只想快进：**
```bash
git fetch
git merge --ff-only origin/main   # 只允许快进，有分叉就报错（逼你处理）
```

### 强推（危险，但有时候必须）

**为什么不能用 `--force`：**
`git push --force` 会无条件覆盖远程分支，如果别人在你 push 前推过新 commit，会被你直接抹掉，他的工作就丢了。

**正确做法用 `--force-with-lease`：**
```bash
git push --force-with-lease   # 只有远程没人推过新 commit 时才强推，否则报错
```

它先检查远程分支的位置和你本地记录的一致，不一致就拒绝——防止覆盖别人的工作。**记住：永远用 `--force-with-lease`，不用 `--force`。**

### 忽略文件

**`.gitignore` 配置（放在项目根目录，随仓库一起提交）：**
```
# 忽略所有 .log 文件
*.log

# 但不忽略 important.log
!important.log

# 忽略 node_modules 目录
node_modules/

# 忽略 build 目录下所有内容
build/

# 忽略所有 .env，但保留 .env.example
*.env
!.env.example
```

**已经提交的文件再加进 .gitignore 不会生效**，要先取消跟踪：
```bash
git rm --cached 文件名        # 从仓库移除但保留本地文件
git commit -m "停止跟踪 文件名"
# 再加进 .gitignore
```

### 标签（版本发布）

```bash
git tag v1.0.0                        # 轻量标签（只是个指针）
git tag -a v1.0.0 -m "发布说明"        # 带注释标签（推荐，annotated tag）
git tag                               # 查看所有标签
git show v1.0.0                       # 查看某标签详情
git push origin v1.0.0                # 推单个标签
git push --tags                       # 推所有标签
git tag -d v1.0.0                     # 删本地标签
git push origin :refs/tags/v1.0.0    # 删远程标签
```

### 查看历史

```bash
git log --oneline --graph --all       # 最常用：看全部分支的图
git log --author="张三"               # 看某人提交
git log --since="2 weeks ago"         # 最近两周
git log -S "functionName"             # 哪些 commit 增删了某字符串（找函数何时引入）
git log -p -- 文件路径                # 某文件每次改动的 diff
git show <commit>                    # 看某次 commit 的具体改动
git blame 文件名                      # 看每行代码是谁最后改的（追责用）
```

### 深度思考：场景比命令重要

记命令的参数是低效的——记不住、版本会变、查文档更快。真正该记的是**"遇到 X 类问题，大概用哪几个命令组合"**。这份速查的意义不是让你背，而是让你建立"问题 → 命令组合"的索引，遇到问题知道往哪个方向查。

---

## 十一、深度总结

### 统一模型

Git 的所有概念可以归约到一个统一模型：

- **对象**（blob/tree/commit/tag）存数据，按内容哈希去重，不可变
- **指针**（分支/HEAD/tag/远程跟踪分支）存引用，几乎零成本，可移动

所有命令都是这两类操作的组合：
- `commit` = 写新对象 + 移当前分支指针
- `branch` = 新建一个指针文件
- `checkout` = 移 HEAD 指针 + 工作区读出快照
- `merge` = 写新 merge commit + 移当前分支指针
- `rebase` = 把一串 commit 拔下来，基于新基底重新应用，生成新对象
- `reset` = 移当前分支指针到指定 commit
- `revert` = 写一个反向 commit
- `cherry-pick` = 复制某 commit 的改动，生成新 commit 接到当前分支
- `stash` = 把工作区改动暂存起来（不进对象库，存在 .git/refs/stash）
- `push/fetch` = 跨仓库传对象 + 移远程/本地指针

### 设计哲学

Git 的设计取舍可以一句话概括：**用空间换速度、离线、简单**。

- 存全量快照而非增量日志 → 取任意版本 O(1)，但占空间
- 内容寻址去重 + packfile 压缩 → 缓解空间占用
- 分布式对等副本 → 离线可用 + 容灾，但首次 clone 大
- 分支只是指针 → 随便开近乎零成本，但概念抽象难学

每个取舍都有代价，但 Linus 选的是"对 Linux 内核这种大规模协作场景最有利"的那一边——速度和离线比磁盘贵，分支轻量比学习曲线重要。事实证明这个取舍在大多数场景下都成立，这就是 Git 能统治 20 年的原因：**不是功能最全，而是核心设计最对**。

### 一句话记住 Git

> Git 是"对象 + 指针"。对象存内容按哈希去重，指针存引用几乎零成本。所有操作都是移动指针、读写对象。设计哲学是空间换速度、离线、简单。
