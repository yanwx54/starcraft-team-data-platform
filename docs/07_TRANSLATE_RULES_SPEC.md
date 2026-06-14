# TRANSLATE_RULES_SPEC_V1.1

## 项目

韩国星际争霸团战数据自动采集与统计平台

版本：V1.1

状态：需求冻结版

------

# 1. 文档目的

定义系统翻译规则的来源、优先级、存储方式和管理规范。

V1版本仅负责：

- 选手名称翻译
- 地图名称翻译

不涉及其他游戏术语翻译。

------

# 2. 设计原则

## 2.1 唯一中文名称原则

同一对象必须对应唯一中文名称。

例如：

```text
김택용
택용
Bisu
```

统一映射：

```text
老毕
```

禁止出现：

```text
老毕
毕司令
Bisu
金泽龙
```

等多个中文名称同时存在。

------

## 2.2 翻译结果稳定原则

一旦翻译规则确定：

```text
韩文名称
↓
中文名称
```

后续不得自动修改。

避免历史数据出现名称漂移。

------

# 3. 翻译范围

## 3.1 选手翻译

支持：

```text
韩文全名
韩文简称
游戏ID
历史别名
```

统一映射为：

```text
中文名称
```

------

## 3.2 地图翻译

支持：

```text
韩文全称
韩文简称
英文名称
```

统一映射为：

```text
中文名称
```

------

# 4. 翻译优先级

系统严格按照以下顺序执行：

```text
Level 1
translate_rules.md

↓

Level 2
translation_rules数据库

↓

Level 3
保留原文

↓
记录异常
```

------

## 说明

V1取消AI翻译。

原因：

- 选手数量有限
- 地图数量有限
- AI翻译容易产生错误

所有新增翻译由管理员维护。

------

# 5. 选手翻译规则

## 5.1 唯一标识

选手数据库主键：

```text
player_uid
```

------

## 5.2 翻译匹配顺序

系统依次尝试：

```text
韩文全名

↓

韩文简称

↓

历史别名

↓

游戏ID
```

------

匹配成功：

返回：

```text
cn_name
```

------

匹配失败：

记录：

```text
translation_error
```

------

# 6. 地图翻译规则

## 6.1 唯一标识

地图数据库主键：

```text
map_uid
```

------

## 6.2 地图匹配顺序

系统依次尝试：

```text
韩文全称

↓

韩文简称

↓

英文名称
```

------

匹配成功：

返回：

```text
cn_name
```

------

匹配失败：

记录：

```text
map_not_found
```

------

# 7. translate_rules.md格式

## 7.1 选手格式

格式：

```text
韩文全名|韩文简称|中文名
```

示例：

```text
김택용|택용|老毕
```

------

## 7.2 地图格式

格式：

```text
韩文全称|韩文简称|英文名|中文名
```

示例：

```text
네오 실피드|실피|Neo Sylphid|小仙女
```

------

# 8. 数据库存储

## 表名

```text
translation_rules
```

------

## 建表语句

```sql
CREATE TABLE translation_rules (
    id BIGSERIAL PRIMARY KEY,

    rule_type VARCHAR(20) NOT NULL,

    source_text VARCHAR(255) NOT NULL,

    translated_text VARCHAR(255) NOT NULL,

    alias_group VARCHAR(255),

    priority INTEGER DEFAULT 1,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(rule_type, source_text)
);
```

------

## rule_type枚举

仅允许：

```text
player
map
```

------

# 9. 后台管理

管理员可执行：

```text
查看翻译规则

新增翻译规则

修改翻译规则

删除翻译规则

导入翻译规则

导出翻译规则
```

------

# 10. 导入机制

系统启动时读取：

```text
translate_rules.md
```

------

导入逻辑：

```text
存在
↓
跳过

不存在
↓
新增
```

------

禁止：

```text
自动覆盖已有规则
```

------

# 11. 异常处理

## translation_error

触发条件：

```text
未知选手
```

------

记录内容：

```text
原始名称

比赛ID

出现时间
```

------

## map_not_found

触发条件：

```text
未知地图
```

------

记录内容：

```text
原始名称

比赛ID

出现时间
```

------

# 12. 版本管理

translate_rules.md属于核心业务配置。

必须：

```text
纳入Git版本管理
```

------

修改规则：

```text
提交PR

代码审核

合并发布
```

------

# 13. V1范围

V1仅支持：

```text
player
map
```

------

# 14. V2预留

未来如需要扩展：

```text
team

race

unit

building

spell

upgrade
```

可在不修改现有架构的情况下直接扩展。

------

# 15. 验收标准

满足：

```text
选手翻译命中率 = 100%

地图翻译命中率 = 100%

重复译名 = 0

冲突译名 = 0
```

即视为翻译模块验收通过。