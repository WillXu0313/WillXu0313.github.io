---
title: Wireshark分析使用
date: 2025-04-19 07:11:14
categories:
- Network
---

https://blog.csdn.net/fortune_cookie/article/details/90413664

https://www.wireshark.org/docs/wsug_html_chunked/PreAck.html

## IP协议抓包分析学习

Wireshark对一个分组的抓包如下，IP协议首部的版本和首部长度共占用8bit，下方packet bytes是将每个字节使用16进制数表示，例如显示为45对应版本和首部长度。

![image-20250330101350945](https://weiqiang-xu-blog.oss-cn-hangzhou.aliyuncs.com/image-20250330101350945.png)

- 首部长度：4bit，单位是 4 byte

- 区分服务：8bit，被分为两部分，前 6 位是 Differentiated Services Codepoint（DSCP差异化服务代码点），后 2 位是 Explicit Congestion Notification（ECN显式拥塞通知）

  - DSCP：区分不同类型的服务
    - 000000 ：默认服务类型
  - ECN：表示网络拥塞控制能力
    - 00 ：发送方和接收方都不支持ECN，即不具备在网络传输过程中对网络拥塞的通知和响应能力
    - 01 ：发送方支持 ECN，但接收方不支持
    - 10 ：接收方支持 ECN，但发送方不支持；
    - 11 ：双方都支持 ECN

- 总长度：16bit，单位是byte

- 标识（Identification）：16bit， 当一个 IP 数据报的长度超过数据链路层的最大传输单元（MTU）时，就需要对数据报进行分片。标识由源主机确定，用来唯一标识同一数据报，目的主机可以根据标识确定收到的分片属于同一数据报，重新组装数据报。

- 标志（Flags）：3bit，从左到右分别是保留位（Reserved Bit）、不分片位（Don't Fragment Bit，DF）和更多分片位（More Fragments Bit，MF）

  - Reserved Bit：保留位，保留用于扩展，必须设置为0

  - Don't Fragment Bit：标识是否允许分片，由源主机在发送 IP 数据报时根据自身需求和对网络情况的判断来设置的

    - 1：不允许路由器对IP报文进行分片。

      > 如果路由器收到一个长度超过其出接口 MTU 且 DF 位为 1 的数据报时，路由器会丢弃报文，并向源主机发送一个 “目标不可达” 的 ICMP 差错报告报文，告知源主机数据报因不能分片而无法传输

    - 0：允许路由器对IP报文进行分片

  - More Fragments Bit：用于标识分片是否传输完

    - 0：最后一个分片，标识所有分片都已传输
    - 1：除了最后一个分片的其他分片，标识后面还有分片要传输

- 片偏移（Fragment Offset）：片偏移量以 8 字节为单位进行计算

- 生存时间（TTL）：剩余跳的最大数，每经过一个路由器减一

- 协议：上层传输协议

- 首部校验和：用于校验数据完整性

![image-20250330094346167](https://weiqiang-xu-blog.oss-cn-hangzhou.aliyuncs.com/image-20250330094346167.png)

![image-20250330094434762](https://weiqiang-xu-blog.oss-cn-hangzhou.aliyuncs.com/image-20250330094434762.png)

IP协议的首部固定部分有20byte，TCP协议的首部固定部分有20byte