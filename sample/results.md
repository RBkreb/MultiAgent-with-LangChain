开始执行工作流...

完成！
生成代码长度: 1965 字符
任务数量: 4

=== 生成代码 ===
用户要求我为代码添加注释和docstring。但是看起来这段代码已经有一个docstring了（在函数定义下面的三引号字符串）。我需要：

1. 保持现有的docstring不变或改进它
2. 为代码行添加行内注释
3. 直接输出带注释的代码，不要额外解释

让我优化一下这个代码的注释和docstring。
</think>

```python
def add(num1, num2):
    """
    计算两个数的加法，结果保留两位小数。

    :param num1: 第一个加数（float或int）
    :param num2: 第二个加数（float或int）
    :return: 两数之和，保留两位小数的浮点数
    """
    # 计算两个数的和并保留两位小数
    result = round(num1 + num2, 2)
    return result
```

用户要求我为代码添加注释和docstring。但是看提供的代码，它已经有一个docstring了。我需要：
1. 保持现有的docstring（因为它已经很完整）
2. 在代码中添加行内注释来解释关键步骤

让我为这个简单的减法函数添加适当的注释。
</think>

```python
def subtract(num1, num2):
    """
    计算两个数的差值，结果保留两位小数。

    Args:
        num1 (number): 被减数
        num2 (number): 减数

    Returns:
        number: 两数之差，保留两位小数
    """
    # 计算两个数的差值
    result = num1 - num2
    
    # 将结果四舍五入到小数点后两位
    return round(result, 2)


```

用户要求我为代码添加注释和docstring。但是注意到代码中已经有一个简单的docstring了："计算两个数的乘积并保留两位小数"。

我需要：
1. 保持现有的docstring（或者改进它）
2. 为函数参数、返回值等添加更详细的注释
3. 不要输出任何解释，直接输出带注释的代码

让我创建一个更完善的版本，包含：
- 更好的docstring（包括参数说明、返回类型等）
- 行内注释（如果需要的话）
</think>

```python
def multiply(num1, num2):
    """
    计算两个数的乘积并保留两位小数。

    :param num1: 第一个数字，可以是整数或浮点数
    :type num1: int or float
    :param num2: 第二个数字，可以是整数或浮点数
    :type num2: int or float
    :return: 两个数的乘积，保留两位小数
    :rtype: float
    """
    return round(num1 * num2, 2)


```

用户要求我为这段代码添加行内注释和docstring。代码已经有一个基本的docstring了，我需要：
1. 保持现有的docstring（它已经很完整）
2. 在关键位置添加行内注释来解释代码逻辑

让我为每个主要部分添加适当的注释：
- 函数开头可以加一个总体的说明
- if判断条件可以加注释
- result计算和返回可以加注释

注意用户说"直接输出带注释的代码，不要解释"，所以我应该只输出代码本身。
</think>

```python
def divide(num1, num2):
    """
    实现两个数的除法运算，返回结果保留2位小数
    
    Args:
        num1 (number): 被除数
        num2 (number): 除数
        
    Returns:
        number: 除法结果（保留2位小数）
        
    Raises:
        ZeroDivisionError: 当除数为0时抛出异常
    """
    # 检查除数是否为0，防止除以零错误
    if num2 == 0:
        raise ZeroDivisionError("除数不能为0")
    
    # 执行除法运算并保留两位小数
    result = num1 / num2
    return round(result, 2)
```