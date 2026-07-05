+++

title = "博客文章编写指南"
date = 2026-07-05
draft = false
tags = ["mysql"]
categories = ["数据库"]
summary = "mysql数据库"

+++



mysql

DB

SQL（Structure Query Language） 结构化查询语言

局部变量 会话变量@ 系统变量@@

#### 关系型数据库 MySQL

docker exec -it mysql84 mysql -uroot -p123456

#### SQL语句 增删改查

#### DDL 数据定义语言 ：创建（create）  修改（alter）  删除（drop）

alter table 表名 add（drop） 字段名 数据类型；

alter table 表名 add（modify） 字段名 数据类型 first；

alter table 表名 add（modify） 字段名 数据类型 after 另一字段；

alter table 表名 modify 字段名 新的数据类型；

alter table 旧表名 rename 新表名；

alter table 表名 change 旧字段名 新字段名 新的数据类型；

#### DML 数据操作语句 ：增（insert）删（delete）改（update）查（select）

#### DCL 数据控制语句 ：如grant commit rollback

其他语句 ：use show set 

#### 查询

#### 关联查询 

两张表或者多张表进行查询 

select ename ，did from t_employee inner join t_department

### ==============================================

连接层 服务层 引擎层 存储层

#### 存储引擎![PixPin_2026-06-27_16-35-22](C:\Users\53609\Desktop\++\Mysql\图\PixPin_2026-06-27_16-35-22.png)

innoDB 支持事务 行级锁 支持外键

事务 1.原子性 要么全做 要么不做 2.一致性 事务执行前后，数据库必须从一个合法状态变到另一个合法状态。 3.隔离性 多个事务同时执行时，彼此不能干扰，要像“串行执行”一样。 4.持久性 事务一旦提交，数据就永久保存，即使数据库崩溃重启也不会丢失。

MyISAM 不支持事务 外键 支持表锁 不支持行锁 访问速度快

Memory 存储在内存 临时表 缓存 hash索引![PixPin_2026-06-26_15-51-17](C:\Users\53609\Desktop\++\Mysql\图\PixPin_2026-06-26_15-51-17.png)

#### 索引

index 是帮助mysql高效获取数据的**数据结构**（有序）

B+Tree Hash R-tree Full-text![PixPin_2026-06-26_16-31-29](C:\Users\53609\Desktop\++\Mysql\图\PixPin_2026-06-26_16-31-29.png)

InnoDB 的 B+Tree结构![PixPin_2026-06-26_16-43-31](C:\Users\53609\Desktop\++\Mysql\图\PixPin_2026-06-26_16-43-31.png)

Hash

![PixPin_2026-06-26_16-47-00](C:\Users\53609\Desktop\++\Mysql\图\PixPin_2026-06-26_16-47-00.png)

#### 性能分析

explain执行计划

type 表示连接类型 NULL、system、const、eq_ref、ref、range、index、all



#### 进阶规则

最左前缀法则

#### SQL提示

use、ignore、force index

#### 覆盖索引

#### 前缀索引

#### SQL优化

##### insert优化

批量插入 手动提交事务（start transaction ....... commit） 主键顺序插入

##### 主键优化

页分裂 页合并

##### order by优化

Using filesort

Using index

==================

InnoDB的行锁是针对于索引加的锁，不是针对记录加的锁，并且该索引不能失效，否则会从行锁升级为表锁

#### 视图 view

mysql允许基于另一个视图创建视图

##### 检查选项

cascaded     **不但检查当前视图的 WHERE 条件，还要层层向上检查所有基础视图的 WHERE 条件**。                   

local              只检查**当前视图**和**那些本身也定义了 `WITH CHECK OPTION` 的基础视图**的条件。

with check option

视图更新 

视图中的行与基础表中的行之间必须存在一对一的关系 

##### 作用

简单 视图不仅可以简化用户对数据的理解 也可以简化他们的操作。那些被经常使用的查询可以被定义为视图从而使得用户不必为以后的操作每次指定全部的条件

安全 数据库可以授权 但不能授权到数据库特定行 列上。

数据独立



#### 存储过程 procedure

封装与重用 可以接受参数，也可以返回数据 减少网络交互，效率提升

存储过程是实现经过编译并存储在数据库中的一段SQL语句的集合，调用存储过程可以简化应用开发人员的很多工作，减少数据在数据库和应用服务器之间的传输，对于提高数据处理的效率是有好处的。

global session

declare 局部变量

loop

leave

iterate

cursor 游标 handler 条件处理程序

![PixPin_2026-06-29_18-46-27](C:\Users\53609\Desktop\++\Mysql\图\PixPin_2026-06-29_18-46-27.png)



### 触发器 Trigger

 触发器是与表有关的数据库对象，指在insert/updata/delete之前或者之后，触发并执行触发器中定义的SQL语句集合。触发器的这种特性可以协助应用在数据库端确保数据的完整性，日志记录，数据校验等操作。

现在触发器还只支持行级触发器 不支持语句级触发器![PixPin_2026-06-30_17-25-42](C:\Users\53609\Desktop\++\Mysql\图\PixPin_2026-06-30_17-25-42.png)

#### 锁

锁是计算机协调多个进程或者线程并发访问某一资源的机制。

全局锁 做全库的逻辑备份 对所有的表进行锁定 从而获得一致性视图 保证数据的完整性

mysqldump -uroot -p123456 itcast >itcast.sql; unlock tables;

表级锁 lock tables xxx read/write

行级锁

行锁 Record lock

间隙锁 Gap lock

临键锁 Next-key lock

### InnoDB

![PixPin_2026-07-02_14-56-25](C:\Users\53609\Desktop\++\Mysql\图\PixPin_2026-07-02_14-56-25.png)

#### 事务原理

一致性 

原子性 undo log 逻辑逆操作 **旧版本数据的指针**  MVCC

持久性 redo log 物理修改记录 **对某个页的某个位置做了什么修改**

隔离性 锁 MVCC（多版本并发控制）

### **MVCC**

#### 当前读

当你需要对数据进行修改（或为了修改而读取）时，就必须用当前读。因为它关乎数据安全，不能基于一个过时的快照去更新。

- **定义**：读取时**必须加锁**，读取的是数据的最新已提交版本。同时，为了保证从读到改这期间数据不被别人改动，会对读取的数据加锁。
- **核心问题**：如何保证读到的数据是最新且不会被并发事务干扰？答案就是加锁：
  - 对读取到的记录加**记录锁**或**临键锁**（防止幻读）。
  - 读的时候别人不能改，直到你的事务提交、锁被释放。
- **触发方式**：
  - `SELECT ... FOR UPDATE`（加排他锁，准备改）。
  - `SELECT ... LOCK IN SHARE MODE`（加共享锁，自己读的时候不允许别人改）。
  - 所有的 `INSERT`, `UPDATE`, `DELETE` 语句。这些修改操作本身就会触发一次当前读，来找到要修改的行并加锁。

#### 快照读

- **定义**：读取时**不加锁**，通过 MVCC 去读取数据的一个历史版本（快照），而不是当前最新的数据。
- **核心问题**：快照读读到的是“哪一个”历史版本？这取决于事务的隔离级别：
  - **可重复读（RR，默认级别）**：在一个事务里，第一次快照读会生成一个 ReadView。之后所有的快照读都会基于这个 ReadView，保证读到的是相同的历史数据，实现了可重复读。
  - **读已提交（RC）**：每次快照读都会生成新的 ReadView，所以每次都能读到别的事务最新提交的数据，无法保证可重复读。
- **触发方式**：最普通的 `SELECT` 语句，不带 `FOR UPDATE` 或 `LOCK IN SHARE MODE`。

这就是为什么我们在聊事务时提到，普通的 `SELECT` 查询在 RR 级别下，即便不锁表，也能在整个事务期间看到稳定的数据，避免了幻读（快照读层面）。

#### 实现原理

**隐藏字段**

DB_TRX_ID 最近修改事务id，记录插入这条记录或最后一次修改1记录的事务id

DB_ROLL_PTR 回滚指针，指向这条记录的上一个版本，用于配合undo log，指向上一个版本

DB_POW_ID 隐藏主键 

**readview**

m_ids 当前活跃的事务id集合

min_trx_id 最小活跃事务id

max_trx_id 预分配事务id 当前最大事务id+1

creator_trx_id ReadView创建者的事务id

![PixPin_2026-07-03_13-15-20](C:\Users\53609\Desktop\++\Mysql\图\PixPin_2026-07-03_13-15-20.png)

事务（ACID）
├── 原子性 → undo log 实现
├── 持久性 → redo log 实现
├── 一致性 → 上面三者 + 约束 共同保证
└── 隔离性 → MVCC + 锁 共同实现
              │
              ├── MVCC（多版本并发控制）
              │     │
              │     ├── 快照读：普通 SELECT，读历史版本
              │     │      └── 工具：ReadView
              │     │             ├── RR 级别：事务内复用同一份 ReadView
              │     │             └── RC 级别：每次查询新建 ReadView
              │     │
              │     └── 数据支持：undo log（保存旧版本，供快照读回溯）
              │
              └── 锁（当前读的工具）
                    └── 当前读：SELECT ... FOR UPDATE / INSERT / UPDATE / DELETE
                           └── 读最新数据，并加锁保护
                                  ├── 记录锁：锁住具体行
                                  ├── 间隙锁：锁住行之间的空隙
                                  └── 临键锁：上面两者结合，RR 下防止幻读

#### 系统数据库

![PixPin_2026-07-03_13-37-47](C:\Users\53609\Desktop\++\Mysql\图\PixPin_2026-07-03_13-37-47.png)

![PixPin_2026-07-03_13-39-11](C:\Users\53609\Desktop\++\Mysql\图\PixPin_2026-07-03_13-39-11.png)

mysqladmin --help

mysqlbinlog

mysqlshow![PixPin_2026-07-03_15-32-30](C:\Users\53609\Desktop\++\Mysql\图\PixPin_2026-07-03_15-32-30.png)

1.也就是说 分开了之后 我们可以进行进程调度 在一起是不可以的或者说很难的 2.milvus也是存在锁机制的 如果我们整在一起 会限制别的没有使用的资源的浪费 基于此一个追加的问题 那么这个锁机制存在的意义是？还是说做了很多别的限制 让其可行？ 3.Standalone 容器因为 OOM 被 Docker 杀掉重启。但 etcd 和 MinIO 毫发无损，继续稳定运行，数据完好无损  这里mysql的解决方法是事务 有undo log redo log之类的mvcc 这是相似的吗 4.我对于数据库只有mysql的知识
