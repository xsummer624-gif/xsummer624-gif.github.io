+++
title = "拟合"
date = 2026-07-07
draft = false
tags = ["机器学习", "特征工程", "笔记"]
categories = ["机器学习"]
math = true
+++
```python
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error

# 设置中文字体
plt.rcParams["font.sans-serif"] = ["KaiTi", "SimHei"] # 增加 SimHei 作为备用
plt.rcParams["axes.unicode_minus"] = False

def polynomial(x, degree):
    """构成多项式，返回 [x^1, x^2, ..., x^n]"""
    # 确保 x 是二维数组以支持广播，然后水平拼接
    x = np.atleast_2d(x)
    return np.hstack([x**i for i in range(1, degree + 1)])

# 1. 生成随机数据
X = np.linspace(-3, 3, 300).reshape(-1, 1)
y = np.sin(X) + np.random.uniform(-0.5, 0.5, 300).reshape(-1, 1)

fig, ax = plt.subplots(1, 3, figsize=(18, 5))

# 绘制原始散点图
for i in range(3):
    # 使用 ravel() 展平为一维数组，确保散点正确绘制
    ax[i].plot(X.ravel(), y.ravel(), "yo", alpha=0.5, label="真实数据散点")

# 划分训练集和测试集
x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 创建线性回归模型
model = LinearRegression()

# ================= 子图 0: 欠拟合  =================
model.fit(x_train, y_train)
y_pred1 = model.predict(x_test)
# 绘制拟合直线 (使用 ravel 展平)
x_line = np.array([[-3], [3]])
ax[0].plot(x_line.ravel(), model.predict(x_line).ravel(), "c", linewidth=2, label="拟合直线")
ax[0].set_title("欠拟合 (Degree=1)")
ax[0].text(-2.8, 1.2, f"测试集 MSE: {mean_squared_error(y_test, y_pred1):.4f}")
ax[0].text(-2.8, 0.9, f"训练集 MSE: {mean_squared_error(y_train, model.predict(x_train)):.4f}")
ax[0].legend()

# ================= 子图 1: 恰好拟合 =================
x_train2 = polynomial(x_train, 5)
x_test2 = polynomial(x_test, 5)
model.fit(x_train2, y_train)
y_pred2 = model.predict(x_test2)
# 绘制拟合曲线 (使用 ravel 展平)
X_poly5 = polynomial(X, 5)
ax[1].plot(X.ravel(), model.predict(X_poly5).ravel(), "k", linewidth=2, label="拟合曲线 (5次)")
ax[1].set_title("恰好拟合 (Degree=5)")
ax[1].text(-2.8, 1.2, f"测试集 MSE: {mean_squared_error(y_test, y_pred2):.4f}")
ax[1].text(-2.8, 0.9, f"训练集 MSE: {mean_squared_error(y_train, model.predict(x_train2)):.4f}")
ax[1].legend()

# ================= 子图 2: 过拟合 =================
x_train3 = polynomial(x_train, 20)
x_test3 = polynomial(x_test, 20)
model.fit(x_train3, y_train)
y_pred3 = model.predict(x_test3)
# 绘制拟合曲线 (使用 ravel 展平)
X_poly20 = polynomial(X, 20)
ax[2].plot(X.ravel(), model.predict(X_poly20).ravel(), "r", linewidth=2, label="拟合曲线 (20次)")
ax[2].set_title("过拟合 (Degree=20)")
ax[2].text(-2.8, 1.2, f"测试集 MSE: {mean_squared_error(y_test, y_pred3):.4f}")
ax[2].text(-2.8, 0.9, f"训练集 MSE: {mean_squared_error(y_train, model.predict(x_train3)):.4f}")

ax[2].set_ylim(-2.5, 2.5)
ax[2].legend()

plt.tight_layout()
plt.show()
```


​    
![png](5_%E6%8B%9F%E5%90%88_files/5_%E6%8B%9F%E5%90%88_0_0.png)
​    

