---
title: JavaSE
date: 2025-04-19 07:11:14
categories:
- Java
---

白马：https://www.itbaima.cn/document/jviyz2hsht9ete5k

JDK1.8安装：https://blog.csdn.net/weixin_44084189/article/details/98966787

笔记规定：非主线内容使用引用记录

# 面向对象基础

对象的创建过程？以`MyClass obj = new MyClass(10, "Hello");`为例——

1. 声明：`MyClass obj`声明指向类的引用变量
2. 实例化：`new`关键字触发对象的实际创建过程，为新对象分配内存空间，并返回对该对象的引用
3. 初始化：
   - 默认初始化：对象创建后其成员变量被赋予默认值（数值类型为0或false，对象引用为null等），
   - 显式初始化：（手动规定的默认值方法被执行，如`String name = test();` ）
   - 构造代码块：构造代码块按照顺序被执行，形如不在任何方法下也不是静态的`{}`
   - 构造方法：接着调用构造方法，有自定义构造方法就调用，否则调用默认无参构造方法
   - 继承问题：类有继承时，会从父类逐级向下初始化，按照上述顺序执行，直到当前类的构造方法被执行完毕
4. 对象就绪：整条语句执行完成，可以使用对象进行操作

**注意**：静态成员（包括静态变量和静态初始化块）按照它们在源代码中的出现顺序进行初始化



静态变量与静态方法？

属于类，不属于对象，静态方法只能直接访问静态变量。

所有被标记为静态的内容，会在类刚加载的时候就分配，而不是在对象创建的时候分配，所以说静态内容一定会在第一个对象初始化之前完成加载。

在Java中使用一个类之前，JVM并不会在一开始就去加载它，而是在需要时才会去加载（优化）一般遇到以下情况时才会会加载类：

- 访问类的静态变量，或者为静态变量赋值
- new 创建类的实例（隐式加载）
- 调用类的静态方法
- 子类初始化时
- 其他的情况会在讲到反射时介绍



# 面向对象高级

## 内部类

创建在内部的类，内部类可以通过`外部类名.this`语法来显式地使用这个外部类引用。

### 成员内部类

在Java中，外部类能够访问内部类（无论是静态内部类还是非静态内部类）的成员变量，但需要通过内部类的一个实例来访问这些成员。不过，需要注意的是访问的方式取决于内部类的类型：

1. **非静态内部类（成员内部类）**：这类内部类与外部类的实例相关联，因此不能直接访问其成员，必须通过创建内部类的一个实例来访问其成员。
2. **静态内部类**：如果内部类被声明为`static`，则它可以包含静态成员，并且可以直接通过类名访问这些静态成员，不需要外部类的实例。

eg：非静态内部类，需要创建实例，注意Test构造方法需要new一个Inner对象。

```java
package org.example;

public class Test {

    private final String name;
    private final Inner inner;

    public Test(String name, String innerName) {
        this.name = name;
        this.inner = new Inner(innerName);
    }

    public void testGetInner() {
        System.out.println(inner.name);
    }

    public class Inner{
        private final String name;

        public Inner(String name) {
            this.name = name;
        }

        public void test(){
            System.out.println(name+", I am inner class!");//就近原则
            System.out.println(this.name+", I am inner class!");//this就近是Inner
            System.out.println(Test.this.name+", I am inner class!");//指明了test
        }
    }
}

```

```java
package org.example;

public class Main {
    public static void main(String[] args) {
        Test test = new Test("xwq","will");
        Test.Inner inner = test.new Inner("weiqiang.xu");
        test.testGetInner();
        inner.test();
    }
}
```

### 静态内部类

> `static`关键字主要用于成员（如变量、方法）、内部类（包括静态内部类）和嵌套类（nested class），以表明它们是属于类本身的，而不是属于类的某个特定实例。

static表明它们是**属于类本身**，但是想要使用内部静态类的变量和方法，还是需要new一个实例对象（类不实例化用个鬼）。

同时static属于类本身的特性也决定了Inner类无法访问Test类的非静态成员。但是受影响的只是外部内容的使用，内部倒是不受影响，还是跟普通的类一样。（我要是直接访问外部类的非静态属性，那到底访问哪个对象的呢？）（内部就是一个普通的类）

eg：

```java
package org.example;

public class Test {

    private final String name;
    public String getName() {
        return name;
    }

    private final Inner inner;

    public Test(String name, String innerName) {
        this.name = name;
        this.inner = new Inner(innerName);
    }

    public void testGetInner() {
        System.out.println(inner.name);
    }



    public static class Inner{
        private final String name;

        public Inner(String name) {
            this.name = name;
        }

        public void test(){
            System.out.println(name+", I am inner class!");//就近原则
            System.out.println(this.name+", I am inner class!");//this就近是Inner
        }
    }
}

```

```java
public class Main {
    public static void main(String[] args) {
        // 创建一个 Test 类的实例，并通过其构造函数初始化了一个 Inner 实例作为成员变量
        Test testInstance = new Test("xwq", "will");
        
        // 独立创建一个 Inner 类的实例，注意这里不需要依赖于 Test 的实例
        Test.Inner standaloneInner = new Test.Inner("weiqiang.xu");

        // 调用 Test 实例的方法，该方法会打印其成员变量 inner 的信息
        testInstance.testGetInner();

        // 调用独立创建的 Inner 实例的方法
        standaloneInner.test();
    }
}
```

可以明显发现这里的打印是不一样的，因为这里其实有两个Inner实例——

- 构造test实例时构造的Inner实例
- 直接构造的Inner实例

> **对象**v**s实例**：大多数情况下这两个术语的语义是相同的，可以平替，都强调是**类的具体化**
>
> - 对象更通用，强调创建并存在于内存中的具体实体
> - 实例多用于强调从哪个类创建的，“这个方法接收一个`User`类的实例作为参数”

### 局部内部类

直接在方法中声明的类，只能在该方法中使用。也需要实例化。

```java
public class Test {
    public void hello(){
        class Inner{   //局部内部类跟局部变量一样，先声明后使用
            public void test(){
                System.out.println("我是局部内部类");
            }
        }
        
        Inner inner = new Inner();   //局部内部类直接使用类名就行
        inner.test();
    }
}
```

### 匿名内部类

- **定义与实例化**：提供一种简洁的方式直接定义（实现接口或继承普通类）并实例化类的对象。无需先显式声明类再创建其实例。
  - **继承普通类**：当匿名内部类基于一个普通类时，它实际上创建了该类的一个子类，并可以覆盖父类中的方法。通常会重写该类中的某些方法（特别是那些抽象方法）。也可以不重写啊

  - **实现接口**：当匿名内部类基于一个接口时，它实际上实现了该接口，并提供了接口中所有抽象方法的具体实现。需要实现接口中的所有抽象方法，有default的抽象方法可以选择是否覆盖。

- **多态性**：通过继承或实现接口体现多态，方便重写父类方法或实现接口方法。

- **适用场景**：适用于仅需一次性使用的对象，减少代码量，提升简洁性。例如，在图形用户界面(GUI)编程中，按钮点击事件的处理程序往往只需要定义一次，使用匿名内部类可以非常方便地完成这一任务。

- **特点**：
  - 没有名字，只能使用一次。
  - 可访问外部类的所有成员；在方法内定义时可访问该方法内的“effectively final”局部变量。
  - 由于没有名字，不能显式定义构造器，但可以通过其父类构造器传入参数。

eg：实现接口的匿名内部类


```java
public abstract class Student {
    public abstract void test();
}

public static void main(String[] args) {
    Student student = new Student() {   //在new的时候，后面加上花括号，把未实现的方法实现了
        @Override
        public void test() {
            System.out.println("我是匿名内部类的实现!");
        }
    };
    student.test();
}
```

### Lambda表达式

- 标准格式为：`([参数类型 参数名称,]...) ‐> { 代码语句，包括返回值 }`

- 接口中只有一个待实现的抽象方法时，用lambda表达式简化简化匿名内部类
- Stream流、集合的操作，如foreach

```
names.forEach(name -> System.out.println(name));
```

## 方法引用

对Lambda表达式进一步简化，方法引用就是将一个已实现的方法，直接作为接口中抽象方法的实现，前提是定义相同

eg：

```
names.forEach(System.out::println);
```

```
public class Main {
    public static void main(String[] args) {
		Teacher teacher = System.out::println;
		teacher.teach("will");
	}
	
	public interface Teacher {
        void teach(String name);

        default void study(String name) {
            System.out.println(name+", I am default study method");
        }
	}
}


```

如果是普通从成员方法，我们同样需要使用对象来进行方法引用

```
Student student = new Student();
Teacher teacher = student::print;
teacher.teach("will");
```

## 工具类

- **基本数据类型的数组**：使用 `Arrays.copyOf` 进行复制时，由于基本数据类型存储的是具体的值而不是引用，所以这实际上是进行了深拷贝。原数组和新数组之间没有共享的状态，修改一个数组中的元素不会影响另一个数组。
- **对象数组**：使用 `Arrays.copyOf` 对对象数组进行复制时，只会复制对象的引用，而不是对象本身，因此这是浅拷贝。如果对象的内容被修改，这种变化会影响到原数组和新数组中对应的元素，因为它们指向相同的对象。

# 泛型程序设计

- 定义：一个变量类型不确定，故提出泛型。泛型就是一个待定类型，泛型在定义时并不明确是什么类型，而是需要到使用时才会确定对应的泛型类型。

- 泛型的类型

  - 只能使用引用类型，基本类型需要用包装类

  - 注意基本类型构成的数组是引用类型，可以作为泛型使用

    > `Score<int[]> score = new Score<>("will", new int[]{1, 2, 3, 4});`
    >
    > Java到处都是new，正常声明赋值长这样`int[] a = {1,2,3,4};`

- 不只是类，包括接口、抽象类，都是可以支持泛型的，和先前学习的设计基本一样

## 函数式接口

函数式接口特点：有一个抽象方法待实现

### Supplier**供给型函数式接口**

获取需要的对象，只有一个get抽象方法需要实现，简直不要太简单。例子看Consumer中的使用

```
@FunctionalInterface
public interface Supplier<T> {
    T get();
}
```

### **Consumer消费型函数式接口**

**功能**：andThen对一个对象建立起消费链，accept调用执行消费链。只要明确功能就好了，原理搞不懂也没关系。跟目前适配工作中的config先定义好转换关系，再使用get获取到参数的思想很想——都是先层层嵌套定义好规则，最后一次性调用。

源码如下：

- 核心：不断实现accept方法来实现消费者链的添加
- 关键：andThen将先前Consumer的accept行为添加到一个新创建的Consumer中，最后一个Consumer调用accept就能实现整个消费者链的执行

```
@FunctionalInterface
public interface Consumer<T> {
    void accept(T t);    //这个方法就是用于消费的，没有返回值

    default Consumer<T> andThen(Consumer<? super T> after) {   //这个方法便于我们连续使用此消费接口
        Objects.requireNonNull(after);
        return (T t) -> { accept(t); after.accept(t); };//关键！返回一个用lambda新创建的Consumer，新Consumer的accept方法是个大集成——先调用 使用andThen方法的对象的accept方法，再调用传入的after的accept方法
    }
}
```

`andThen()`让我理解了半天，断点debug+理解后终于搞懂了。因为lambda写法特别多，看着很抽象，不好理解具体创建了什么，返回了什么，下面举个例子来解释具体创建的Consumer。

先上结论——在整个链式调用的过程中，确实创建了5个 `Consumer` 实例：（这里的匿名是在main内来看的，其实符合Consumer也是匿名的）

1. 初始的 `APPLE_CONSUMER`（`Consumer1`）
2. 第一个匿名 `Consumer`（`Consumer2`）
3. 第一个复合 `Consumer`（`Consumer3`）
4. 第二个匿名 `Consumer`（`Consumer4`）
5. 最终的复合 `Consumer`（`Consumer5`）

```
public class Apple {
    public void hello(){
        System.out.println("我是苹果！");
    }

	//分别实现一个Supplier和Consumer
	
	//方法引用，Supplier中的get直接用Apple的new来实现
    private static final Supplier<Apple> APPLE_SUPPLIER = Apple::new;
    //lambda创建一个实现accept方法的Consumer1
    private static final Consumer<Apple> APPLE_CONSUMER = apple -> System.out.println(apple+"好吃！");

    public static void main(String[] args) {
        Apple apple = APPLE_SUPPLIER.get();
        apple.hello();

        APPLE_CONSUMER
                .andThen(apple1 -> System.out.println(apple1+"1"))
                .andThen(apple1 -> System.out.println(apple1+"2"))
                .accept(apple);
    }
}
```

```
	APPLE_CONSUMER
                .andThen(apple1 -> System.out.println(apple1+"1"))//Consumer1调用andThen，传入Consumer2
                .andThen(apple1 -> System.out.println(apple1+"2"))
                .accept(apple);
```

```
@FunctionalInterface
public interface Consumer<T> {
    void accept(T t);    //这个方法就是用于消费的，没有返回值

    default Consumer<T> andThen(Consumer<? super T> after) {   //这个方法便于我们连续使用此消费接口
        Objects.requireNonNull(after);
        return (T t) -> { accept(t); after.accept(t); };//返回新创建的Consumer3
    }
}
```

```
		.andThen(apple1 -> System.out.println(apple1+"2"))//Consumer3调用andThen，传入Consumer4
```

```
@FunctionalInterface
public interface Consumer<T> {
    void accept(T t);    //这个方法就是用于消费的，没有返回值

    default Consumer<T> andThen(Consumer<? super T> after) {   //这个方法便于我们连续使用此消费接口
        Objects.requireNonNull(after);
        return (T t) -> { accept(t); after.accept(t); };//返回新创建的返回Consumer5
    }
}
```

```
		.accept(apple)//执行Consumer5的accept
```

其实最后执行accept的Consumer的accept实际内容精简后是这样的——

```
void accept(Apple apple){
	System.out.println(apple+"好吃！");
	System.out.println(apple+"1"));
	System.out.println(apple+"2"));
}
```

当然编译器应该不是直接优化成这样的，而是逐层解析对象往下执行的。按照我debug的经验来讲是这样的，事实上也应该是这样。

想起来zstack的chain好像就是消费链模式？

### Function函数型函数式接口

这个接口消费一个对象，然后会向外供给一个对象（前两个的融合体）

```java
@FunctionalInterface
public interface Function<T, R> {
    R apply(T t);   //这里一共有两个类型参数，其中一个是接受的参数类型，还有一个是返回的结果类型

    default <V> Function<V, R> compose(Function<? super V, ? extends T> before) {
        Objects.requireNonNull(before);
        return (V v) -> apply(before.apply(v));
    }

    default <V> Function<T, V> andThen(Function<? super R, ? extends V> after) {
        Objects.requireNonNull(after);
        return (T t) -> after.apply(apply(t));
    }

    static <T> Function<T, T> identity() {
        return t -> t;
    }
}
```

直接看怎么用

```java
	private static final Function<Integer, String> INTEGER_STRING_FUNCTION = Object::toString;
    public static void main(String[] args) {
   
        String str = INTEGER_STRING_FUNCTION
                .compose((String s) -> s.length() )
                .apply("lbwnb");//这里返回，调用compose中传入的对象的apply方法
        System.out.println(str);

        boolean result = INTEGER_STRING_FUNCTION
                .andThen(String::isEmpty)//这里返回
                .apply(1);
        System.out.println(result);

        Function<String, String> function = Function.identity();//返回输入
        System.out.println(function.apply("???"));//原封不动返回
    }
```

### Predicate断言型函数式接口

 接收一个参数，然后进行自定义判断并返回一个boolean结果

```java
@FunctionalInterface
public interface Predicate<T> {
    boolean test(T t);    //这个方法就是我们要实现的

    default Predicate<T> and(Predicate<? super T> other) {
        Objects.requireNonNull(other);
        return (t) -> test(t) && other.test(t);
    }

    default Predicate<T> negate() {
        return (t) -> !test(t);
    }

    default Predicate<T> or(Predicate<? super T> other) {
        Objects.requireNonNull(other);
        return (t) -> test(t) || other.test(t);
    }

    static <T> Predicate<T> isEqual(Object targetRef) {
        return (null == targetRef)
                ? Objects::isNull
                : object -> targetRef.equals(object);
    }
}
```

就不动手敲了，用法比较好懂。

## 判空包装

Optional的使用，用法可多了

```
private static void test(String str){
        Optional
                .ofNullable(str)   //将传入的对象包装进Optional中
                .ifPresent(s -> System.out.println("字符串长度为："+s.length()));
        //如果不为空，则执行这里的Consumer实现
    }
```

# 集合类

（这些类的操作纯看和逐个手动实验十分枯燥，没有耐心手敲，非常不想学，总觉得有更重要的事情要做。写代码就是写作，要勇于实践，不能纸上谈兵，一时没有兴趣那就每天抽点时间来写，三分钟热度也要学的更多！！！）

## ArrayList

基本操作注意事项

创建方式：三种——创建空列表、指定容量、从collection创建

```
List<Integer> b =new ArrayList<>();
List<Integer> c =new ArrayList<>(5);
List<Integer> d =new ArrayList<>(b);
List<Integer> e =new ArrayList<>(Arrays.asList(1,2,3,4,5));
```

只读与可操作

```
List<String> list = Arrays.asList("A", "B", "C");//只读
List<String> list = new ArrayList<>(Arrays.asList("A", "B", "C"));//可正常操作
```

add添加操作

remove删除操作：注意删开头第一个后结束

## Stream流

工作中遇到再返回来学，先总结几个看到的

- filter：条件过滤
- collect：收集
- sorted：排序
- map：对每个元素映射操作
- limit：限制个数

```
list = list     //链式调用
            .stream()    //获取流
            .filter(e -> !e.equals("B"))   //只允许所有不是B的元素通过流水线
            .collect(Collectors.toList());   //将流水线中的元素重新收集起来，变回List
```

