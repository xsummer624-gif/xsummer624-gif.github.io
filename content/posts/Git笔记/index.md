+++

title = "Git"
date = 2026-07-12
draft = false
tags = ["Git","笔记"]
summary = "Git"

++++



# Git 

## 一、Git 与 GitHub 的关系

- **Git** 是一个分布式版本控制系统（软件），由 Linus Torvalds 开发，运行在本地，无需网络即可工作。
- **GitHub** 是基于 Git 的代码托管平台（网站服务），提供云端仓库托管、协作、Pull Request、Issue 等团队功能。

关系：GitHub 依赖 Git 作为底层版本控制引擎，但 Git 本身不依赖 GitHub——可以用 GitLab、Bitbucket、Gitee 等任意托管平台，也可以纯本地使用。

---

## 二、Git 历史

### 诞生背景
Linux 内核项目早期没有版本控制系统，开发者通过邮件互发补丁，Linus 手动合并。后短暂使用 BitKeeper（商业版本控制系统）。

### 导火索：BitKeeper 事件
BitKeeper 公司因有人试图逆向工程其协议，收回免费授权。Linux 内核社区失去核心开发工具。

### Git 的诞生
Linus 决定自己写一个，设计目标：
1. **速度**：操作必须快
2. **分布式**：每个克隆都是完整仓库，离线可用
3. **数据完整性**：用 SHA-1 校验所有内容
4. **支持大规模协作**：支持成千上万的并行分支

Linus 在 2005 年 4 月 7 日开始开发，**仅用 10 天**写出可用原型。2005 年 7 月将维护工作交给 Junio Hamano（至今仍是核心维护者）。

名字 "Git" 来源：英国俚语中意为"令人不愉快的人"，Linus 自嘲式命名。手册描述为 "the stupid content tracker"。

### 核心设计哲学（与 CVS/SVN 的本质区别）

| 维度 | 传统系统（CVS/SVN） | Git |
|------|---------------------|-----|
| 模型 | 集中式 | 分布式 |
| 存储差异 | 存储文件 delta（增量） | 存储快照（snapshot） |
| 分支 | 重量级，复制目录 | 轻量级，仅一个指针 |
| 离线 | 几乎不可用 | 完全可用 |
| 完整性 | 弱 | SHA-1 内容寻址 |

关键思想：Git 把数据看作一系列快照而非增量差异。每次 commit 存储整个项目树的快照（未改动的文件只存引用），形成 DAG（有向无环图）。

---

## 三、快照（Snapshot）机制

### 快照是什么
快照不是单个文件的内容，而是**整个项目在某一时刻的完整目录结构 + 所有文件内容**。

### 四大对象模型

Git 底层只有四种对象，存储在 `.git/objects/` 中：

1. **blob**：文件内容（不含文件名、不含路径）
2. **tree**：目录结构（文件名 + 权限 + 子项引用）
3. **commit**：快照 + 父提交 + 作者/时间/消息
4. **tag**：annotated tag（带注释的标签，指向某 commit + 说明）

每个对象用 SHA-1 哈希作为唯一标识，文件内容决定哈希值（内容寻址存储 content-addressable storage）。

### 对象间的引用关系
```
        ┌──────────┐
        │  commit  │  一个快照 + 父提交 + 元信息
        └────┬─────┘
             │ 指向
             ▼
        ┌──────────┐
        │   tree   │  顶层目录，列出文件名 + 子目录引用
        └────┬─────┘
             │ 递归引用
      ┌──────┴──────┐
      ▼             ▼
  ┌────────┐   ┌──────────┐
  │  blob   │   │ sub-tree │  blob = 文件内容；sub-tree = 子目录
  └────────┘   └──────────┘
```

### 快照的存储逻辑
- 一个快照（commit）= 一个 tree + 它引用的所有 blob
- 改了某个文件 → 为这个文件新建一个 blob，存完整新内容
- 没改的文件 → tree 里直接填旧 blob 的哈希，那个 blob 一动不动、不重新存

**核心区别**：redo log 存的是"做了什么操作"，Git 存的是"现在长什么样"。Git 是"状态快照"，不是"操作日志"。

### 存储优化
- 改了的文件 → 存一份新的完整内容
- 没改的文件 → 不存，直接引用旧 blob

逻辑上是完整快照（简单直观），物理上是去重存储（节省空间）。

### 为什么 Git 这样设计（空间换速度）
- 相同内容天然去重（内容寻址）
- 取任意历史版本 O(1)，不用回放 diff
- 离线可用
- 分支轻量

代价是磁盘占用相对多，但靠三层优化缓解：
1. **内容寻址去重**：相同内容只存一份
2. **packfile 压缩**：松散对象打包成 .pack，zlib 压缩 + delta 压缩（同文件多版本只存差异）
3. **partial clone**：新版 Git 支持按需拉取 blob

---

## 四、回滚机制

### 回滚 = 换指向，不换 blob，也不新增存储
回滚只是把 HEAD 指针挪到旧 commit，复用早就存好的旧 blob，不新增任何存储。

### 回滚的三种方式

| 方式 | 命令 | 行为 | 适用场景 |
|------|------|------|---------|
| **改写历史** | `git reset --hard commit-X` | 分支指针退回，旧 commit 变悬空 | 本地未 push 的提交 |
| **反向提交** | `git revert commit-X` | 新建一个反向 commit，历史不丢 | 已 push 的公共分支 |
| **保留改动** | `git reset --soft/--mixed` | 指针退回但保留改动在暂存区/工作区 | 撤销 commit 但保留代码 |

### 旧 blob 会被删吗？
短期内不会。Git 会留着，通过 `git reflog` 还能找回。真正删除要满足：
1. 没有任何 commit / 分支 / tag / reflog 指向它（变成不可达对象）
2. 手动或自动执行 `git gc`（垃圾回收）

**Git 里几乎没有真正的删除，只要 commit 过就能找回**。

---

## 五、分支管理

### 关键真相：分支只是一个指针

分支在 Git 里就是 `.git/refs/heads/` 下一个小文件，里面装一个 40 字符的 commit 哈希。

```
.git/refs/heads/main    内容: abc123...   ← main 指向 commit abc123
.git/refs/heads/dev     内容: def456...   ← dev 指向 commit def456
```

创建分支 = 新建一个 41 字节的文件，不复制任何代码，瞬间完成（O(1)）。

对比 SVN：创建分支要复制整个目录到新路径（O(项目大小)）。这就是 Linus 说"分支很便宜，随便开"的原因。

### HEAD 是另一个指针
`.git/HEAD` 文件内容是 `ref: refs/heads/main`，意思是"我现在在 main 分支上"。

| 概念 | 本质 |
|------|------|
| **分支** | 指向某 commit 的指针（会移动） |
| **HEAD** | 指向当前所在分支的指针 |
| **tag** | 指向某 commit 的指针（不移动） |

### 分支创建时发生了什么
1. 在 `.git/refs/heads/` 下新建一个文件（如 dev），内容写当前 commit 哈希
2. 把 `.git/HEAD` 改成 `ref: refs/heads/dev`

**没有新建 tree，没有复制任何 blob，没有复制任何文件内容**。

### 分叉何时发生
分支刚创建时，两个指针指向同一个 commit，没区别。区别出现在你在分支上做新 commit 之后——"分叉"发生在 commit 那一刻，不是 checkout -b 那一刻。

```
commit-1 ← commit-2 ← commit-3
                                ├─ main:  commit-3 → commit-6 → commit-7
                                └─ dev:   commit-3 → commit-4 → commit-5
```

- commit-1、2、3 是两个分支共享的，没有复制，就一份
- 从 commit-3 往后，两条线各自新增自己的 commit

### 合并（merge）

**情况 A：fast-forward（快进合并）**
如果 main 没有新提交，dev 有，直接把 main 指针挪到 dev 的位置。

**情况 B：真合并（产生 merge commit）**
两边都有新提交，Git 做一个新 commit，它有**两个父提交**，把两条线的改动合并。

### 分支的本质
分支不是"从主线复制出来的"，而是"和主线共享同一个历史起点，从某个 commit 开始往后各自生长"。

---

## 六、分支与回滚的关系

两者都是"改指针，不碰数据"的操作，本质上非常相似：

| 操作 | 改了什么 | 动了 blob 吗 |
|------|---------|-------------|
| 切分支 `git checkout dev` | HEAD 指向 dev | 不动，工作区换内容 |
| 回滚 `git reset --hard commit-X` | HEAD/当前分支指向 commit-X | 不动，工作区换内容 |

区别在于动哪个指针 + 历史怎么处理：
- **回滚**：当前分支指针本身往后退（同一条线上纵向后退）
- **分支**：新建指针，从某 commit 另起一条线（在不同指针间横向切换）

类比：
- 回滚 = 临时退回去
- 分支 = 长期驻扎在那个点上继续开发
- tag = 给某个点起固定名字

### 分支保护历史不被回滚破坏
```
错误做法：直接在 main 上 commit，不行就 reset --hard → 已 push 会破坏别人的历史
正确做法：
  1. git checkout -b experiment    # 开个分支试
  2. 在 experiment 上随便 commit
  3. 不行？git checkout main; git branch -D experiment   # 删分支，main 完全没动
  4. 行？git checkout main; git merge experiment       # 合进来
```

---

## 七、Git 的物理结构（.git 目录）

```
.git/
├── HEAD                 # 当前在哪个分支（指针的指针）
├── config               # 本仓库配置（用户名、远程地址等）
├── refs/                # 所有"指针"的存放处
│   ├── heads/           #   本地分支指针（每个分支一个文件）
│   ├── remotes/         #   远程分支指针（如 origin/main）
│   └── tags/            #   标签指针
├── objects/             # 所有对象存储（blob/tree/commit/tag）
│   ├── pack/            #   打包压缩后的对象（节省空间）
│   └── xx/...           #   松散对象（按 SHA-1 前两位分目录）
├── index                # 暂存区（二进制文件，下次 commit 的清单）
├── logs/                # reflog（指针移动的历史，找回"丢失"提交用）
│   └── HEAD
│   └── refs/heads/main
└── hooks/               # 钩子脚本（pre-commit 等触发点）
```

---

## 八、Git 的逻辑分层：四大区域

```
┌──────────────┐   git add    ┌──────────────┐  git commit  ┌──────────────┐  git push  ┌──────────────┐
│  工作区       │ ────────────▶│   暂存区      │ ───────────▶│  本地仓库    │ ─────────▶│  远程仓库    │
│ Working Dir  │              │   Index      │             │  .git/objects│           │  GitHub      │
│              │◀─────────────│              │◀───────────│             │◀──────────│             │
└──────────────┘ git checkout └──────────────┘ git reset   └──────────────┘ git fetch └──────────────┘
   你编辑的文件               "下次提交清单"              commit 历史链               别人的仓库
```

### 各部分职责

| 区域 | 是什么 | 职责 |
|------|--------|------|
| **工作区** | 你眼睛看到、编辑器能改的文件 | 你干活的地方，修改先发生在这里 |
| **暂存区** | `.git/index` 二进制文件 | 记录"下次 commit 要包含哪些文件的哪个版本"——购物车清单 |
| **本地仓库** | `.git/objects/` | 保存项目的全部历史快照 |
| **远程仓库** | GitHub/GitLab 服务器 | 协作中转站，多人同步的桥梁 |

暂存区为什么需要：让你精确控制一次 commit 包含哪些改动（改了 3 个文件，只 add 其中 2 个提交）。

---

## 九、引用层（refs）：把对象组织成可用历史

`.git/refs/` 是 Git 的"导航系统"。

| 引用类型 | 位置 | 作用 |
|---------|------|------|
| **分支** | `refs/heads/main` | 指向某条开发线的最新 commit |
| **远程跟踪分支** | `refs/remotes/origin/main` | 记录"上次 fetch 时远程 main 在哪" |
| **标签** | `refs/tags/v1.0` | 给某个 commit 起固定名字 |
| **HEAD** | `.git/HEAD` | 指向当前所在分支 |

光有一堆对象没用，你得知道"现在在哪"、"有哪些线"。Git 所有高级操作（checkout、merge、reset、rebase）本质上都是移动这些指针。

---

## 十、本地与 GitHub 的关系

### 真相：本地和 GitHub 不是"分工存储"，而是对等副本

`git clone` 会把所有 blob、tree、commit 全部下载到本地 `.git/objects/`。本地仓库和远程仓库结构完全一样，都是完整的。

```
你的电脑                              GitHub 服务器
.git/objects/                        服务器仓库
  ├─ blob-111 (a.txt v1)              ├─ blob-111 (a.txt v1)
  ├─ blob-222 (a.txt v2)             ├─ blob-222 (a.txt v2)
  ├─ tree-xxx                         ├─ tree-xxx
  ├─ commit-abc                       ├─ commit-abc
  └─ ... 全部历史                     └─ ... 全部历史
```

两边存的东西一模一样，只是各自的"当前指针位置"可能不同。

### 为什么还需要 GitHub？

GitHub 不是"存东西的地方"，而是**协作的中转站**：

| 需求 | 本地仓库做不到 | GitHub 的作用 |
|------|---------------|--------------|
| **多人协作** | 你电脑里的 commit 怎么发给同事？ | 提供一个大家都连得上的中心节点 |
| **备份** | 电脑坏了，本地仓库没了 | 远程有副本 |
| **分享/开源** | 让全世界看到你的代码 | 托管平台 + 社交功能 |
| **CI/CD、PR、Issue** | 纯 Git 没有 | 平台附加功能 |

GitHub 的核心价值是"协作"和"托管"，不是"存储"。可以用 GitLab、Gitee、自建服务器替代——Git 本身不依赖任何远程平台。

### push / fetch 做的事
- `git push`：把本地多出来的 commit/tree/blob 复制一份发给 GitHub，GitHub 存进去，再把它的 main 指针前移
- `git fetch`：反过来，把 GitHub 多出来的对象拉到本地存起来

传输的是"差异部分的对象"，但传输完之后两边又各自完整。

---

## 十一、辅助系统

| 系统 | 位置 | 作用 |
|------|------|------|
| **reflog** | `.git/logs/` | 记录指针移动历史，即使 commit 不在分支上也能找回 |
| **config** | `.git/config` | 仓库级配置（远程地址、用户名等），优先级：命令参数 > 仓库级 > 用户级 > 系统级 |
| **hooks** | `.git/hooks/` | 特定事件触发的脚本（pre-commit、post-merge 等） |
| **packfile** | `.git/objects/pack/` | 把松散对象打包压缩成 .pack + .idx，大幅节省空间和加速 clone |

---

## 十二、一次 commit 的完整流程

1. 你在工作区改了 `a.txt`
2. `git add a.txt` → Git 计算 a.txt 的新哈希，存成新 blob，在 index 里更新"a.txt → 新哈希"
3. `git commit -m "fix"`：
   - 用 index 当前的内容生成一个新 tree（顶层目录快照）
   - 生成新 commit 对象（父 = 当前 HEAD 指向的 commit，tree = 刚生成的 tree）
   - 把当前分支指针（如 main）从旧 commit 移到新 commit
   - 记一条 reflog
4. `git push origin main` → 把本地新对象（commit/tree/blob）和 ref 更新发给远程，远程也做同样的"对象存储 + 指针移动"

整个 Git 就是"对象存数据 + 指针存引用 + 几个区做数据流转"三层逻辑的组合。

## 核心思想总结

> Git 的核心是**"对象 + 指针"**：
> - blob/tree/commit 是内容对象（存数据，按哈希去重）
> - 分支/HEAD/tag 是指针（存引用，几乎零成本）
>
> 所有操作（commit、branch、merge、reset、rebase、checkout）本质上都是**移动指针 + 读写对象**。
>
> 设计哲学是**"空间换速度/离线/简单"**：
> - 存全量快照而非增量日志 → 取任意版本 O(1)
> - 内容寻址去重 + packfile 压缩 → 缓解空间占用
> - 分布式对等副本 → 离线可用 + 容灾
> - 分支只是指针 → 随便开，近乎零成本
