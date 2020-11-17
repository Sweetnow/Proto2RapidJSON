# Proto2RapidJSON
![Python package](https://github.com/Sweetnow/Proto2RapidJSON/workflows/Python%20package/badge.svg) [![codecov](https://codecov.io/gh/Sweetnow/Proto2RapidJSON/branch/main/graph/badge.svg)](https://codecov.io/gh/Sweetnow/Proto2RapidJSON)
---

### 简介
本工具旨在利用[proto](https://developers.google.com/protocol-buffers/docs/proto3)文件生成基于[RapidJSON](https://rapidjson.org/)的JSON文件解析与序列化的C++工具。
- 本工具只会支持最基本的类proto语法，但保证其强类型属性；
- 本工具生成的C++代码只依赖RapidJSON与C++11 STL；
- 本工具支持//注释。

### 基本格式
```protobuf
package test;

message B {
  bool isok;
}

message A {
  double x;
  int32 y;
  repeated B b;
}
```

对应的JSON文件（message A对应的）为

```json
{
    "x": 1.24,
    "y": 123,
    "b": [
        {
            "isok": true
        },
        {
            "isok": false
        }
    ]
}
```

*注：暂不允许可选属性，但允许额外的属性（不会被解析）。*

生成的C++文件应该包含结构体与接口如下

```c++
struct B {
    bool isok;
    B& FromString(const char* str);
    B& FromValue(const rapidjson::Value& v);
    std::string ToString();
    std::string ToPrettyString();
    rapidjson::Value ToValue(rapidjson::Document::AllocatorType& allocator);
}

struct A {
    double x;
    int y;
    std::vector<B> b;
    A& FromString(const char* str);
    A& FromValue(const rapidjson::Value& v);
    std::string ToString();
    std::string ToPrettyString();
    rapidjson::Value ToValue(rapidjson::Document::AllocatorType& allocator);
}
```
### 保留字

```
message, package, {}, ;, repeated, double, int32, int64, uint32, uint64, float, bool, string, //
```

### 语法

```
Program -> Package Message*
Package -> "package" id ";"
Message -> "message" id "{" Element* "}"
Element -> Type id ("=" num) ";" | "repeated" Type id ("=" num) ;"
Type -> id | "double" | "float" | "int32" | "uint32" | "int64" | "uint64" | "bool" | "string"
```

注1：`("=" num)`仅用于兼容`proto`文件格式，不起任何作用

注2：`id`允许包含数字与下划线，且不允许数字开头

### 使用

在完成安装`pip install .`后，可以使用如下指令执行：

```bash
python -m proto2rapidjson -i <INPUT> -o <OUTPUT>
```

### 计划

- [x] 添加序列化的模板
- [x] 编写CLI，生成二进制文件并支持`pip install .`
- [x] 完善测试与代码覆盖率测试
- [x] 禁止相同id
