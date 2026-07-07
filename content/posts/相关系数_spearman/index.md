+++
title = "相关系数_spearman"
date = 2026-07-07
draft = false
tags = ["机器学习", "特征工程", "特征选择"，“笔记”]
categories = ["机器学习"]
math = true
+++
通过计算特征与目标变量或特征之间的相关性，筛选出高相关性特征或剔除冗余特征

斯皮尔曼相关系数


```python
import pandas as pd
```


```python
# 定义数据
# 每周学习时长
X = [[5],[8],[10],[12],[15],[3],[7],[9],[14],[6]]
# 数学考试成绩
y = [55,65,70,75,85,50,60,72,80,58]
```


```python
X = pd.DataFrame(X)
y = pd.Series(y)
print(X.shape)
print(y.shape)
```

    (10, 1)
    (10,)



```python
print( X.corrwith(y,method='spearman'))
```

    0    0.987879
    dtype: float64

