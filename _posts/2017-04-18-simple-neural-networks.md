---
title: 人工智障系列·简单的神经网络
layout: post
category: learn
image: /media/kizuna-ai.jpg
summary: 来实现一个超级简单的神经网络吧
---

参考于《机器学习》周志华。

神经网络的基本原理还是挺平易近人的，知道偏导数就能看懂。

人肉写个代码其实意外地简单，用到 NumPy，不过只有一个隐层。

每个神经元的输入是这样：

$$
\text{HiddenInput}_{\text{HiddenIndex}}=\sum_{\text{InputIndex}}^{\text{InputSize}}{\text{HiddenValue}_{\text{InputIndex}, \text{HiddenIndex}}\times\text{Input}_{\text{InputIndex}}}
$$


然后减掉每个神经元的阈值，塞到形如sigmod的激活函数然后就输出。 <!--more-->

显然因为两层全联接，所以不可能真的模拟神经元一样创建一大堆node object。这里所有的计算都是可以矩阵化的。

公式推导什么的这篇文章就不涉及了，具体根据书上推导，反正这类内容也挺多的，我写的东西也就自己会看…主要是编码上的内容。

----------

[`neural_networks.py#L23`](https://github.com/tioover/bendan/blob/2ddb24ea88bdde58ba3e5c56d63ed1f28c6b64a4/neural_networks.py)

23 行开始的 `_output` 函数为了计算单个神经元的输出，以供后面求导。

代码里涉及到矩阵的部分，最需要时刻清楚的是每个矩阵的行和列数，以及行和列代表什么，否则忘了转置什么的搞错维度了还是会很麻烦的。虽然写出来很简洁。

每一个输入当成一个向量，但实际上是一个 1x输入数 的矩阵，而权值写成 前一层输入数x本层神经元数 的矩阵。

这样只需要一个矩阵乘法就能得到输出了，乘出来就是 1x本层神经元数。

矩阵比密密麻麻的连线好看多了，当成表格就很好理解，第 m 行就是第 m 个输入分量，第 n 列就是第 n 个神经元。

----------

[`neural_networks.py#L31`](https://github.com/tioover/bendan/blob/2ddb24ea88bdde58ba3e5c56d63ed1f28c6b64a4/neural_networks.py#L31)

31行：计算输出层和隐层间的梯度值。

因为sigmoid的导数是 $$f'(x) = f(x)(1-f(x))$$，所以可以直接这样写：

~~~python
@np.vectorize
def d_sigmoid(y):
    return y*(1.0-y)
~~~

在更新权值的代码中，把神经元输出 y 反喂给sigmoid的导数。在知道 y 的情况下，简单地就能知道 $$f'(x)$$ 了。

所得出的 g 就是更新神经元要用到的梯度值。

----------

[`neural_networks.py#L33`](https://github.com/tioover/bendan/blob/2ddb24ea88bdde58ba3e5c56d63ed1f28c6b64a4/neural_networks.py#L33)

33行：类似，我们求输入层和隐层间的的梯度值。

需要隐层的输出 b，喂给 `d_sigmoid` 就得到隐层输入下的导数了。然后这行也是链式法则的产物，意义和BP算法的推导这里就不涉及了

NumPy 默认乘法的语义不是线性代数乘法，在不同的时候可以解释成标量乘法、一一对应相乘、或者如果行向量和列向量相乘的话会被解释成两个对角向量的矩阵乘法……反正这个可能和数学的直觉不一样但是从编码来说挺方便的。[Broadcasting - NumPy v1.12 Manual](https://docs.scipy.org/doc/numpy/user/basics.broadcasting.html) 想要矩阵乘的话可以用 @ 运算符。

----------

[`neural_networks.py#L35`](https://github.com/tioover/bendan/blob/2ddb24ea88bdde58ba3e5c56d63ed1f28c6b64a4/neural_networks.py#L35)

最后是更新参数，也只需要根据推导出的更新公式，各种梯度值乘上学习率然后更新原有的参数就是了。注意也大量用到了NumPy的怪异乘法，否则写起来还很麻烦呢。

最后的效果可以看这里，[`neural_networks.ipynb`](https://github.com/tioover/bendan/blob/master/neural_networks.ipynb)

XOR 不说了，类似Hello World的东西。

简单的西瓜分类，一开始按照书上的插图，隐层设成了两个神经元，结果预测结果和瞎猜没有区别，实际上至少要设成三个。
