# CRAWLER_SPEC_V1.0

## 项目

韩国星际争霸团战数据自动采集与统计平台

版本：

V1.0

适用数据库：

DATABASE_V1.0

------

# 1. 爬虫总体架构

## 流程图

```text
Scheduler
    ↓
ListCrawler
    ↓
ArticleCrawler
    ↓
HtmlArchive
    ↓
Parser
    ↓
Translator
    ↓
DatabaseWriter
    ↓
StatisticsRefresh
```

------

# 2. 采集目标

## 列表页

```text
https://eloboard.com/men/bbs/board.php?bo_table=pro_league
```

作用：

发现最新比赛文章。

------

## 详情页

示例：

```text
https://eloboard.com/men/bbs/board.php?bo_table=pro_league&wr_id=2455
```

作用：

获取比赛全部数据。

------

# 3. 调度规则

## 主任务

执行时间：

```text
每天10:00
```

------

## 补采任务

执行时间：

```text
10:30
11:00
12:00
```

------

## 任务名称

```text
daily_match_crawler
```

------

# 4. 列表页采集规则

## 获取内容

提取：

```text
wr_id
title
article_url
publish_date
```

------

## wr_id解析

示例：

```text
wr_id=2455
```

提取：

```text
2455
```

------

## 去重逻辑

查询：

matches.wr_id

存在：

```text
跳过
```

不存在：

```text
进入详情页采集
```

------

# 5. 详情页采集规则

## 第一步

保存原始HTML

写入：

raw_articles

------

## 第二步

开始解析。

------

# 6. 比赛基础信息解析

提取：

```text
比赛标题

比赛日期

wr_id

source_url
```

写入：

matches

------

# 7. 队伍解析

解析：

```text
队伍A

队伍B
```

------

## 队伍不存在

创建：

teams

生成：

```text
team_uid
```

格式：

```text
TEAM000001
```

------

## 队伍存在

直接关联。

------

# 8. 选手解析

## 提取

```text
韩文名

游戏ID

种族

所属队伍
```

------

## 玩家匹配流程

```text
translate_rules
↓
player_aliases
↓
players
↓
新建玩家
```

------

## 新玩家规则

生成：

```text
player_uid
```

格式：

```text
P000001
```

------

## 玩家别名

自动写入：

player_aliases

------

# 9. 赛制识别规则

系统支持：

```text
BO7
KOF
ACE
```

------

## BO7识别

满足：

```text
7局固定对战
```

判定：

```text
stage_type=BO7
```

------

## KOF识别

满足：

```text
擂台赛模式

胜者留场
败者下场
```

判定：

```text
stage_type=KOF
```

------

## ACE识别

满足：

```text
ACE
결승전
최종전
```

关键词。

判定：

```text
stage_type=ACE
```

------

# 10. 地图解析

提取：

```text
韩文地图名
```

------

## 地图匹配流程

```text
maps.kr_name
↓
maps.en_name
↓
maps.cn_name
```

------

## 未匹配

新增：

maps

状态：

```text
is_active=true
```

------

# 11. 对局解析

每局比赛生成：

match_details

------

提取：

```text
game_no

player_a

player_b

map

winner

loser

stage
```

------

## game_no规则

BO7：

```text
1~7
```

------

KOF：

```text
按出现顺序
```

编号。

------

ACE：

```text
999
```

固定值。

------

# 12. 胜负解析

规则：

```text
赢家
↓
winner_player_id

输家
↓
loser_player_id
```

------

默认比分：

```text
1 : 0
```

------

# 13. 奖金解析

页面存在：

```text
玩家
奖金
```

区域。

------

提取：

```text
player_id
prize_amount
```

------

写入：

prize_pool

------

# 14. 翻译规则

优先级：

```text
translate_rules.md
↓
历史数据库
↓
AI翻译
↓
原文
```

------

## 玩家翻译

输出：

```text
cn_name
```

------

## 地图翻译

输出：

```text
cn_name
```

------

# 15. 数据冻结规则

首次采集成功后：

```text
matches

match_details

prize_pool
```

不再更新。

------

即使：

```text
ELOBOARD修改数据
```

也不覆盖。

------

# 16. 数据异常规则

## 玩家未识别

写入：

data_issues

类型：

```text
player_not_found
```

------

## 地图未识别

类型：

```text
map_not_found
```

------

## 奖金异常

类型：

```text
prize_error
```

------

## 解析失败

类型：

```text
crawl_error
```

------

# 17. HTML变更检测

记录：

```text
html_hash
```

建议：

SHA256

------

当：

```text
同一wr_id

hash变化
```

记录日志。

但不更新业务数据。

------

# 18. 日志规范

INFO

```text
开始采集
完成采集
```

------

WARNING

```text
翻译缺失

地图缺失
```

------

ERROR

```text
页面访问失败

HTML结构变化

数据库写入失败
```

------

# 19. 失败重试机制

页面访问失败：

```text
重试3次
```

------

重试间隔：

```text
5秒
```

------

# 20. 首次历史回补

范围：

```text
2026-01-01
至当前日期
```

------

执行方式：

```text
按wr_id升序
```

导入。

------

# 21. 幂等性要求

重复执行：

```text
同一wr_id
```

不得产生：

```text
重复比赛

重复奖金

重复选手
```

------

依赖：

```text
wr_id唯一索引
```

保证。

------

# 22. 验收标准

成功率：

```text
≥99%
```

------

漏采率：

```text
≤1%
```

------

重复数据：

```text
0
```

------

异常数据：

```text
全部进入
data_issues
```

------

# 模块划分

```text
crawler/
├── scheduler.py

├── list_crawler.py

├── article_crawler.py

├── parser.py

├── translator.py

├── database_writer.py

├── issue_handler.py

├── html_archive.py

└── statistics_refresh.py
```

作为Codex生成代码时的标准目录结构。