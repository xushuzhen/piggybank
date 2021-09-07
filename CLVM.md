# CLVM 理解

我们写的clvm代码想运行，需要先用run编译成一堆括号的那种底层代码，然后用brun运行底层代码，得到结果

比如目录中的 factorial.clvm 和 square.clvm
（square.clvm改为了使用常量作为主函数参数，所以brun square.clvm的底层代码时不用传参）

先执行run编译 

```
run factorial.clvm
```

得到底层代码

```
(a (q 2 2 (c 2 (c 5 ()))) (c (q 2 (i (= 5 (q . 1)) (q 1 . 1) (q 18 (a 2 (c 2 (c (- 5 (q . 1)) ()))) 5)) 1) 1))
```

然后用brun运行底层代码
(brun '底层代码' '(参数)')

```
brun '(a (q 2 2 (c 2 (c 5 ()))) (c (q 2 (i (= 5 (q . 1)) (q 1 . 1) (q 18 (a 2 (c 2 (c (- 5 (q . 1)) ()))) 5)) 1) 1))' '(5)'
```

得到运算结果

```
120
```

## brun 底层语言

1. 关键字
   q：引用，比如想使用100这个数字 (q . 100)，也可以引用数组(q . (80 90 100))
   i：if判断语句(i (第一个括号：判断条件) (第二个括号：满足条件执行) (第三个括号：不满足条件执行))
   f：返回第一个元素
   r：返回除第一个元素的其他元素
   c：把多个元素组成一个list

2. 运算符
   
   ```
   ; 有+ - * /四种运算
   ; 写法是运算符在最前面，然后是两个参数

   brun '(- (q . 6) (q . 5))'
   ; 结果是 1

   brun '(/ (q . 3) (q . 2))'
   ; 结果是1
   
   brun '(/ (q . 3) (q . -2))'
   ; 结果是-2
   ```
   需要注意的是，这里整数都： 向下取整！向下取整！向下取整！

   不支持浮点数

3. 二叉树结构
   
   ```
   brun '1' '(("deeper" "example") "data" "for" "test")'
   ```

   第一层根节点

   1:根节点，返回(("deeper" "example") "data" "for" "test")

   第二层叶子节点

   2:节点1的左叶子节点("deeper" "example")

   3：节点1的右叶子节点"data" "for" "test"

   第三层叶子节点

   4：节点2的左叶子节点"deeper"

   5：节点3的左叶子节点"data"

   6：节点2的右叶子节点"example"

   7：节点3的右叶子节点"for" "test"

   第四层叶子结点

   8：节点4左叶子节点，因为节点4已经是最小原子，不能再进行拆分，所以会报错FAIL: path into atom "deeper"

   11：节点7的左叶子节点"for"

   15：节点7的右叶子节点"test"

## run 高级语言

1. 函数、宏和常量
   
   ```
    (mod (arg_one arg_two)
        (defconstant const_name value)
        (defun function_name (parameter_one parameter_two) *function_code*)
        (defun another_function (param_one param_two param_three) *function_code*)
        (defun-inline utility_function (param_one param_two) *function_code*)
        (defmacro macro_name (param_one param_two) *macro_code*)

        (main *program*)
    )
   ```

   defconstant：常量

   defun：函数

   defun-inline：内联函数

   defmacro：宏

2. 需要注意的点
   
   函数可以在代码中引用自己，但宏和内联函数不能

   函数和宏都可以引用其他函数、宏和常量

   Macros that refer to their parameters must be quasiquoted with the parameters unquoted

   （猜测意思：使用宏的时候，参数必须标记为unquoted）

   内联函数通常更效率（更快？），除非

   ```
   (defun-inline foo (X) (+ X X)) (foo (* 200 300))
   ```
   这样会在加法的两个参数上，重复运行两次乘法