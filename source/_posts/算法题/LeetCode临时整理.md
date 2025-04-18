---
title: LeetCode临时整理
date: 2025-01-25 07:49:30
tags: LeetCode
categories:
- Algorithm
---

# LeetCode刷题记录

## 记录模板

解法xxx：xxx

1. 思路
2. 犯错
3. 代码

## 0001 两数之和

O(n)思路：使用哈希表记录原数和原数的下标，扫描一遍，去哈希表中寻找另一半数，找不到就记录原数和原数的下标，找到据返回。
错误：忽略了map查找有两个返回值的特点，返回值可以更简洁，不一定要设计变量记录
```Go
func twoSum(nums []int, target int) []int {
 hashTable := make(map[int]int)
 for i, num1 := range nums {
     if j, ok := hashTable[target-num1]; ok {
         return []int{i, j}
     }
     hashTable[num1] = i
 }
 return nil
}
```

## 0002 两数相加

思路：思路清晰，就是模拟整个相加的过程。对两个链表进行遍历，首先确定相加的数字，然后求和，最后将结果添加结点到目标链表中。结束遍历后要对进位位进行检查，如果有进位就要再创建一个结点。
错误：为了使链表信息可保存（添加结点的时候不会丢失当前结点），我们创建了一个空的头结点，在添加结点时是添加下一个结点。同时处理完记得后移。
```Go
func addTwoNumbers0(l1 *ListNode, l2 *ListNode) *ListNode {
 head := new(ListNode)
 cur, n1, n2, carry := head, 0, 0, 0
 for l1 != nil || l2 != nil {
     //确定相加数
     if l1 == nil {
         n1 = 0
     } else {
         n1 = l1.Val
         l1 = l1.Next
     }
     if l2 == nil {
         n2 = 0
     } else {
         n2 = l2.Val
         l2 = l2.Next
     }
     //相加
     sum := n1 + n2 + carry
     carry = sum / 10
     //添加结点
     cur.Next = &ListNode{Val: sum % 10}
     cur = cur.Next
 }
 //处理最后是否要进位
 if carry == 1 {
     cur.Next = &ListNode{Val: 1}
 }
 return head.Next
}
```
## 0003 无重复字符的最长子串

  思路：双指针+哈希表记录（也可以叫做滑动窗口，其实就是双指针，字符串常用双指针），head指针的含义是不重复子串的开头。我们使用一个数组标记访问过的字符，用来存放遇到重复字符时，从什么地方开始重新扫描确定无重复子串。这种使用数组来记录失败时回退的位置的做法，和KMP的getNext函数似乎很类似。
  ```Go
  func lengthOfLongestSubstring(s string) int {
   var m [128]int //128个ASCII码，存下标位置+1，默认为0,用于更新无重复子串的开头
   head, maxLen := 0, 0
   for i := 0; i < len(s); i++ {
       head = max(head, m[s[i]])//更新head到无重复子串的开头，也就是舍弃掉重复的字符串
       m[s[i]] = i + 1//标记出现过的字母的下一位置
       maxLen = max(maxLen, i-head+1)//更新最长无重复子串的长度
   }
   return maxLen
  }
  ```

这其实算是优化过后的做法，使得head可以直接跳转到下一位，而不是单纯用哈希表标记字符是否出现，跳转的操作更少，代价就是我们每遇到一个字符就要更新一次最长长度，但是少了很多的判断，计算机执行应该更快。
  我们来看看LeetCode官方的题解，还要涉及到删除哈希表的记录
  ```Go
  func lengthOfLongestSubstring(s string) int {
   // 哈希集合，记录每个字符是否出现过
   m := map[byte]int{}
   n := len(s)
   // 右指针，初始值为 -1，相当于我们在字符串的左边界的左侧，还没有开始移动
   rk, ans := -1, 0
   for i := 0; i < n; i++ {
       if i != 0 {
           // 左指针向右移动一格，移除一个字符->就是把左侧重复字符的哈希记录删了，
           //原来重复的字符（即rk+1处的字符）在右侧就不算重复了
           //算是一种更新手段吧，方便后续右指针更新
           delete(m, s[i-1])
       }
       for rk + 1 < n && m[s[rk+1]] == 0 {
           // 不断地移动右指针
           m[s[rk+1]]++
           rk++
       }
       // 第 i 到 rk 个字符是一个极长的无重复字符子串
       ans = max(ans, rk - i + 1)
   }
   return ans
  }

func max(x, y int) int {
    if x < y {
        return y
    }
    return x
}
  ```
## 0004 HHH寻找两个正序数组的中位数

•简单粗暴思想：正序合并数组。有空数组直接处理非空数组；没有空数组，合并数组。按照大小添加元素，发现任意一个数组元素全部添加完后，只添加另一数组元素。
错误点：思路不清晰，数组越界处理不当。

```Go
//正序合并数组，求中位数->中间元素
func findMedianSortedArrays(nums1 []int, nums2 []int) float64 {
    m, n := len(nums1), len(nums2)
    //若存在空数组，非空数组即为合并数组
    if m == 0 {
        if n%2 == 0 {
            return float64(nums2[n/2-1]+nums2[n/2]) / 2
        } else {
            return float64(nums2[n/2])
        }
    }
    if n == 0 {
        if m%2 == 0 {
            return float64(nums1[m/2-1]+nums1[m/2]) / 2
        } else {
            return float64(nums1[m/2])
        }
    }
    //数组均非空，开始合并数组
    l := m + n
    merge := make([]int, l)
    for count, i, j := 0, 0, 0; count < l; count++ {
        //若一数组所有元素均已添加，后续直接添加另一组所有元素后结束
        if i == len(nums1) {
            for ; j != n; j++ {
                merge[count] = nums2[j]
                count++
            }
            break//for后j等于n，下标j已越界，应该结束，否则39行出错
        }
        if j == len(nums2) {
            for ; i != m; i++ {
                merge[count] = nums1[i]
                count++
            }
            break//下标i已越界，应该结束
        }
        //两数组都没有处理完，按照大小依次添加元素
        if nums1[i] < nums2[j] {
            merge[count] = nums1[i]
            i++
        } else {
            merge[count] = nums2[j]
            j++
        }
    }
    //按照合并数组长度的奇偶找中位数
    if l&1 == 0 {
        return float64((merge[l/2] + merge[(l-1)/2])) / 2
    } else {
        return float64(merge[l/2])
    }
}
```
•稍微变换：找数字，一个一个排除，处理到找到中位数即可
 a < m && (b == n || nums1[a] < nums2[b])利用了或运算逻辑短路实在是妙啊。b==n说明了已经越界了，此时就返回了1，后续访问也不再执行，而b不等于n时后续会访问数组比大小，写的很简洁。
核心就在for循环中的if语句逻辑处理上
```Go
func findMedianSortedArrays(nums1 []int, nums2 []int) float64 {
    m, n := len(nums1), len(nums2)
    l := m + n
    var left, right, a, b int
    for i := 0; i < l/2+1; i++ { //找数
        left = right
        //nums1没找完的前提下，nums1[a]比较小，从nums1中存数，a后移。防止越界即num2要可访问
        //还是一个逻辑上的问题吧，就是什么时候从nums1取数字，什么时候从nums2取数字的问题
        if a < m && (b == n || nums1[a] < nums2[b]) {
            right = nums1[a]
            a++
        } else { //nums2没找完的前提下，从nums2中存数，b后移
            right = nums2[b]
            b++ //nums2找到最后一个后，b==n，再进if会数组越界，要预防越界->利用逻辑短路
        }
    }
    if l%2 == 0 {
        return float64(left+right) / 2
    } else {
        return float64(right)
    }
}
```
•转换思路：查找第k小数（k=l/2）
•定义思路：切分数组
```Go
//切分数组
/*
    切分nums1---nums1[midA-1] | nums1[midA]
    切分nums2---nums2[midB-1] | nums2[midB]
    ---------------------------------------
    0<=midA<=m   0<=midB<=n  midB=(m+n+1)/2-midA  遇到类似下标小心数组越界
    1.从切分角度想，切分不能超过一半，midA是自变量，要限制midA小于等于总长的一半，因此midA的所有取值都要小于总长一半，故 m<=(m+n)/2
    2.从不等式角度想，利用不等式可加性也可求出m和n的关系
    3.直接想会不会越界，(m+n+1)/2有总长一半之大，那么midA要小于等于一半长
    所以默认nums1长度较小
    ---------------------------------------
    low指向处理数组的下界元素，high指向上界元素+1（表征长度），high-low即为长度
*/
func findMedianSortedArrays(nums1 []int, nums2 []int) float64 {
    m, n := len(nums1), len(nums2)
    if m > n {
        return findMedianSortedArrays(nums2, nums1)
    }
    low, high, k, midA, midB := 0, m, (m+n+1)/2, 0, 0
    for low <= high {
        midA = low + (high-low)>>1
        midB = k - midA
        if midA > 0 && nums1[midA-1] > nums2[midB] { //不越界前提下左移
            high = midA - 1 //二分查找的标准写法，现在midA-1这个数是右边的第一个数，刚好是处理数组的上界+1
        } else if midA < m && nums1[midA] < nums2[midB-1] { //不越界前提下右移
            low = midA + 1
        } else {
            //合适切分
            break
        }
    }
    fmt.Println("low high", low, high)
    var midLeft, midRight int //切分的左右值
    //处理切分左边值
    if midA == 0 {
        midLeft = nums2[midB-1]
    } else if midB == 0 {
        midLeft = nums1[midA-1]
    } else {
        midLeft = max(nums1[midA-1], nums2[midB-1])
    }
    //总长度为奇数只要midLeft
    if (m+n)&1 == 1 {
        return float64(midLeft)
    }
    //处理切分右边值
    if midA == m {
        midRight = nums2[midB]
    } else if midB == n {
        midRight = nums1[midA]
    } else {
        midRight = min(nums1[midA], nums2[midB])
    }
    //总长度为偶数
    return float64(midLeft+midRight) / 2
}
```
5. No.0011盛水
题目：
给定一个长度为 n 的整数数组 height 。有 n 条垂线，第 i 条线的两个端点是 (i, 0) 和 (i, height[i]) 。找出其中的两条线，使得它们与 x 轴共同构成的容器可以容纳最多的水。返回容器可以储存的最大水量。说明：你不能倾斜容器。
双指针思路：关键在于缩减搜索空间。使用两个指针，一左一右，每次移动短板，只有移动短板才有可能使得水槽短板变长，高度才可能变长。移动长板的话，短板会不变或者变短。
```Go
func maxArea(height []int) int {
    i, j := 0, len(height)-1
    high, max:=0, 0
    for i != j {
        //更新高度、最大值
        high = min(height[i], height[j])
        if high*(j-i) > max {
            max = high * (j - i)
        }
        //每次移动短板寻找max
        if height[i] > height[j] {
            j--
        } else {
            i++
        }
    }
    return max
}
```

