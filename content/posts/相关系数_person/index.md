+++
title = "相关系数_person"
date = 2026-07-07
draft = false
tags = ["机器学习", "特征工程", "特征选择", “笔记”]
categories = ["机器学习"]
math = true
+++
通过计算特征与目标变量或特征之间的相关性，筛选出高相关性特征或剔除冗余特征

皮尔逊相关系数


```python
import pandas as pd
```


```python
# 读取数据
data = pd.read_csv('../../data/advertising.csv')
print(data.head())
print(data.shape)
```

       Unnamed: 0     TV  Radio  Newspaper  Sales
    0           1  230.1   37.8       69.2   22.1
    1           2   44.5   39.3       45.1   10.4
    2           3   17.2   45.9       69.3    9.3
    3           4  151.5   41.3       58.5   18.5
    4           5  180.8   10.8       58.4   12.9
    (200, 5)



```python
# 数据预处理 去掉第一列
data.dropna(inplace=True)
data.drop(data.columns[0], axis=1, inplace=True)
print(data.head())
print(data.shape)
```

          TV  Radio  Newspaper  Sales
    0  230.1   37.8       69.2   22.1
    1   44.5   39.3       45.1   10.4
    2   17.2   45.9       69.3    9.3
    3  151.5   41.3       58.5   18.5
    4  180.8   10.8       58.4   12.9
    (200, 4)



```python
# 定义特征X和标签y
X = data.drop("Sales",axis=1)
y = data["Sales"]
print(X.shape)
print(y.shape)
```

    (200, 3)
    (200,)



```python
# 计算皮尔逊相关系数
r = X.corrwith(y,method="pearson")
print(r)
```

    TV           0.782224
    Radio        0.576223
    Newspaper    0.228299
    dtype: float64



```python
# 计算皮尔逊相关系数矩阵
corr_matrix = data.corr(method="pearson")
print(corr_matrix)
```

                     TV     Radio  Newspaper     Sales
    TV         1.000000  0.054809   0.056648  0.782224
    Radio      0.054809  1.000000   0.354104  0.576223
    Newspaper  0.056648  0.354104   1.000000  0.228299
    Sales      0.782224  0.576223   0.228299  1.000000



```python
# 可视化显示
import seaborn as sns
sns.heatmap(corr_matrix,annot=True,fmt=".2f",cmap="coolwarm")
```

    <matplotlib.axes._subplots.AxesSubplot at 0x1f723cc2220>






![png](2_%E7%9B%B8%E5%85%B3%E7%B3%BB%E6%95%B0_person_files/2_%E7%9B%B8%E5%85%B3%E7%B3%BB%E6%95%B0_person_8_1.png)
    

