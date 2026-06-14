# 韩国星际争霸团战数据自动采集与统计平台

## 项目需求分析文档（PRD）

### 版本信息

| 项目    | 内容                  |
| ----- | ------------------- |
| 项目名称  | 韩国星际争霸团战数据自动采集与统计平台 |
| 版本    | V1.3（V1.1 + V1.2 合并完整版） |
| 编写日期  | 2026-06-13          |
| 数据来源  | ELOBOARD职业团战数据      |
| 开发模式  | Web系统 + 自动采集服务      |
| 目标用户  | 星际争霸颜究院             |
| 部署信息  | 服务器IP、域名等记录于独立《部署配置文档》，不在本PRD中列出 |

### 版本沿革说明

* **V1.0**：初始需求稿。
* **V1.1**：补充采集补抓机制、数据库字段冗余处理、翻译改名/确认流程、统计口径定义、权限/备份/告警/时区等非功能性需求。
* **V1.2**：调整项目定位为"自动采集 → 自动翻译 → 自动统计 → 数据分析 → 网页展示"，移除AI战报、微信公众号推送相关内容；新增原始网页存档、历史数据回补、选手唯一身份体系、赛季体系、地图池管理、数据质量中心。
* **V1.3（本版本）**：合并V1.1与V1.2，并补充以下内容：
  1. 历史数据重新导入的幂等性与字段覆盖规则（避免覆盖人工已确认数据）。
  2. `player_uid` 的用途说明与生成规则。
  3. 赛季归属（`season_id`）的自动判定规则及边界情况处理。
  4. 地图池与对局地图不匹配时的处理流程（接入数据质量中心）。
  5. `raw_articles` 与业务表的关联关系及解析失败处理流程。
  6. `data_issues` 的状态枚举与处理流程细节，新增 `season_not_found`、`map_pool_mismatch` 异常类型。
  7. V1.2新增统计展示项（近期状态榜、种族胜率、奖金趋势等）的口径定义。
  8. 明确V1.1中权限管理、告警机制、时区/备份策略在V1.3中继续生效。
  9. 更新待确认事项清单，移除已在V1.2/V1.3中解决的问题，标注剩余问题。
  10. 给出全部数据表的完整最终字段定义（汇总表）。

---

# 一、项目背景

韩国星际争霸职业团战每天都会在 ELOBOARD 网站发布最新比赛结果。

目前需要人工查看网页并整理：

* 团战名单
* 选手对阵情况
* 胜负结果
* 奖金池变化

工作量较大且容易出错。因此需要开发一套自动化系统，实现自动抓取、自动翻译、自动统计、自动展示，形成长期可查询的团战数据中心。

---

# 二、项目目标与定位

## 2.1 总体流程

```text
检查ELOBOARD是否有新文章（支持批量补抓）
    ↓
保存原始HTML（raw_articles）
    ↓
解析比赛数据
    ↓
韩文翻译（含改名/AI待确认处理）
    ↓
写入业务数据库（含赛季归属判定、地图池校验）
    ↓
更新统计数据
    ↓
网页展示
```

## 2.2 项目定位（V1.2调整后）

```text
自动采集 → 自动翻译 → 自动统计 → 数据分析 → 网页展示
```

定位为**长期运营的电竞数据平台**。

本版本**不包含**：

* AI赛事分析 / 自动战报生成 / MVP评选
* 微信公众号联动 / 公众号草稿箱推送 / PushPlus推送 / 企业微信推送

以上内容如未来需要，作为独立的V2.0需求另行评估（见第十七章）。

---

# 三、数据来源与采集合规性

## 3.1 主页面

```text
https://eloboard.com/men/bbs/board.php?bo_table=pro_league
```

系统每天访问该页面，获取文章列表（wr_id、发布日期、标题、链接）。

例如：

```text
https://eloboard.com/men/bbs/board.php?bo_table=pro_league&wr_id=2455
```

## 3.2 采集合规性要求

* 每日固定时段访问一次列表页 + 当日新文章详情页，不进行高频轮询。
* 请求设置合理的 User-Agent，请求间增加随机延时。
* 开发前需确认ELOBOARD服务条款/robots.txt是否对自动化访问有限制，如有限制需调整方案。

---

# 四、数据采集需求

## 4.1 采集触发与补抓机制

系统每天上午10:00执行（时区说明见第十五章）：

```text
访问列表页，获取最近N篇文章（N可配置，默认10）
对比 matches 表中已存在的 wr_id

筛选出未采集的 wr_id 列表（可能为0篇、1篇或多篇）

如果列表为空：
    记录"无新数据"日志，结束

如果列表非空：
    按 wr_id 从小到大依次进入采集流程
```

## 4.2 原始网页存档机制

### 目的

防止ELOBOARD未来页面结构调整导致历史数据无法重新解析，支持解析规则升级和数据修复。

### 流程

```text
获取文章
    ↓
保存原始HTML至 raw_articles（按wr_id upsert）
    ↓
解析比赛数据
    ↓
写入业务数据库
```

### raw_articles 与业务表的关系（V1.3新增说明）

* `raw_articles.parsed_status` 取值：`pending`（已抓取未解析）/ `success`（解析成功）/ `failed`（解析失败）。
* 抓取本身失败（网络错误、页面不可达）记录至 `crawl_log`，**不**写入 `raw_articles`。
* 抓取成功但解析失败（页面结构异常、字段缺失等）：
  * `raw_articles` 记录写入，`parsed_status = failed`。
  * 同时在 `data_issues` 中创建一条 `issue_type = crawl_error`（或新增 `parse_error`，建议拆分以便区分"网络层失败"与"解析层失败"）的记录，关联 `source_table = raw_articles`。
  * 此时 `matches` 表中**不**创建对应记录，避免出现"空壳"比赛数据。
* 解析成功后，`matches`/`match_details` 等业务记录才被创建，`raw_articles.parsed_status` 更新为 `success`。

### 存储说明

`html_content` 字段长期累积会导致数据库体积增长较快，建议：

* 评估是否对HTML内容进行压缩存储（如gzip后存为bytea），或
* 仅存储解析所需的关键DOM片段而非整页HTML（需在"解析规则升级"场景下评估是否够用）。

具体方案在开发阶段确认，PRD层面仅要求"原始数据可追溯、可重新解析"。

## 4.3 历史数据回补机制

### 后台功能：历史数据导入

支持：

```text
指定起始wr_id / 结束wr_id
指定日期范围
```

进行批量导入。

### 导入模式

| 模式   | 触发场景 | 行为 |
| ---- | ---- | ---- |
| 增量模式 | 每日10:00定时执行 | 仅采集 `matches` 表中不存在的新 wr_id |
| 全量模式 | 首次部署、历史补录、数据修复 | 对指定范围内的 wr_id 重新抓取并重新解析 |

### 幂等性与字段覆盖规则（V1.3新增，关键）

全量模式重新导入时，必须遵守以下规则，避免覆盖人工已确认数据：

1. **upsert而非删除重建**：`matches` 按 `wr_id` 唯一索引upsert；`match_details` 按 `(match_id, game_no)` 唯一索引upsert。禁止先删除再插入，以保持 `prize_pool.match_id`、`data_issues.source_id` 等外键引用稳定。
2. **结构性字段允许覆盖**：比分（`score`）、地图（`map_id`）、选手韩文ID关联（`player_a_id`/`player_b_id`）、比赛日期、奖金金额等"从原始页面直接解析得到"的字段，重新解析时以最新解析结果为准。
3. **人工确认字段不被覆盖**：`players.cn_name` 在 `translation_status = confirmed` 时，重新解析流程**不得**修改该字段；如重新解析得到的韩文ID与历史记录不一致（如选手改名），按第五章改名处理流程走，不直接覆盖译名。
4. **冲突记录**：若重新解析结果与现有记录在结构性字段上不一致（如比分从1:0变为0:1），写入 `data_issues`（`issue_type = score_conflict` 等），不自动覆盖，等待人工核对后再决定是否更新。

## 4.4 采集内容

### 4.4.1 团战基本信息

| 字段    | 说明         |
| ----- | ---------- |
| 比赛日期  | yyyy-mm-dd |
| 团战名称  | 网站标题       |
| 奖金金额  | 当天奖金       |
| 比赛链接  | 原始URL      |
| wr_id | 文章ID（唯一索引去重） |
| 赛季归属  | 自动判定，见第七章   |

### 4.4.2 队伍信息

提取队伍名称、队伍积分、队伍奖金，分别写入 `teams`、`team_scores`、`prize_pool`（按队伍维度，见第八章字段说明）。

### 4.4.3 选手信息

| 字段   | 说明 |
| ---- | ---- |
| 韩文ID | 选手韩文显示名 |
| 中文ID | 翻译后中文名 |
| 种族   | Z/P/T |
| 所属队伍（当前） | 写入 `players.current_team_id`，历史归属见 `player_team_history` |

### 4.4.4 对战记录

| 字段   | 示例         |
| ---- | ---------- |
| 比赛序号 | 1          |
| 选手A  | Shuttle    |
| 选手B  | SoulKey    |
| 比赛地图 | MatchPoint |
| 比分   | 1:0        |

> `winner_id` 由程序根据 `score` 和 `player_a_id`/`player_b_id` 推导写入，详见第八章 `match_details` 字段说明。

---

# 五、翻译需求

## 5.1 翻译规则来源与优先级

用户提供 `translate_rules.md`，系统必须严格遵循，并支持后台上传后自动重新加载（无需重启服务）。

优先级：

```text
translate_rules.md
    ↓
历史数据库（players表中已确认的中文译名）
    ↓
AI翻译（结果标记为"待确认"，不直接写入历史库作为标准译名）
```

## 5.2 选手改名/译名变更处理

* 同一选手历史上使用过多个韩文ID：通过 `player_aliases` 表维护"曾用ID → 选手主记录（player_uid）"的映射。
* 译名变更需通过后台手动操作，系统记录变更日志；变更不自动批量改写历史比赛展示数据的原始字段（历史记录引用的是 `player_uid`，展示名实时取 `players.cn_name` 当前值，因此变更后历史记录展示名会自动更新为最新译名——如需"历史记录保留当时译名"的需求，作为待确认事项见第十六章）。

## 5.3 地图翻译字典

地图名称统一中文化，存储于 `map_translation` 表，后台可维护增删改。初始数据：

| 韩文     | 中文    |
| ------ | ----- |
| 제인 도   | 简·道   |
| 옥타곤    | 八角    |
| 매치포인트  | 赛点    |
| 네오 실피드 | 新丝绸之路 |

若解析到的地图名在 `map_translation` 中找不到对应记录，写入 `data_issues`（`issue_type = map_not_found`），暂用原韩文入库，等待人工补充字典。

## 5.4 AI翻译结果确认流程

```text
AI翻译产生译名
    ↓
写入 players 时标记 translation_status = "pending"
    ↓
管理员在"翻译规则管理"模块查看待确认列表
    ↓
确认后：
    - 更新 players.cn_name，translation_status = "confirmed"
    - 可选择是否同步写入 translate_rules.md（供下次优先匹配）
```

---

# 六、选手唯一身份体系

## 6.1 player_uid 的用途（V1.3补充说明）

`players` 表新增 `player_uid` 字段，作为**面向前端展示和URL引用的稳定标识**，与数据库内部自增主键 `id` 解耦：

* `id`：内部主键，仅用于表间外键关联，不对外暴露。
* `player_uid`：格式如 `P000001`，按选手记录创建顺序自动分配，**永久不变**，用于前端选手页URL（如 `/players/P000001`）、API返回结果等对外场景，避免直接暴露自增id。

选手改ID、改译名、转队均不影响 `player_uid`，历史统计数据通过 `id`/`player_uid` 关联，保持连续正确。改名/转队的历史追溯分别由 `player_aliases`、`player_team_history` 表支撑（第五章、第七章）。

## 6.2 设计原则

* `player_uid` 在选手记录创建时生成，不可修改、不可重复使用（即使该选手记录被合并/废弃，编号也不回收）。
* 若发现两条选手记录实际为同一人（如曾误判为不同选手），需通过后台"选手合并"功能处理——此功能的具体交互流程列入第十六章待确认事项。

---

# 七、赛季体系与地图池管理

## 7.1 seasons 赛季表

记录赛季名称及起止日期，例如：

```text
2026 Season 1
2026 Season 2
2027 Season 1
```

## 7.2 赛季归属判定规则（V1.3新增）

`matches.season_id` 的赋值规则：

1. 采集到比赛后，根据 `match_date` 自动匹配 `seasons.start_date <= match_date <= seasons.end_date` 的赛季记录。
2. 若匹配到唯一赛季，自动写入 `season_id`。
3. 若匹配到**多个**赛季（赛季时间重叠）或**未匹配到任何**赛季（赛季间存在空档期），`season_id` 留空，并写入 `data_issues`（`issue_type = season_not_found`），由管理员在后台手动指定赛季。
4. 赛季的起止日期由管理员在赛季管理功能中维护，建议在每个赛季开始前提前配置好，减少 `season_not_found` 的出现频率。

## 7.3 地图池管理

### season_maps 表

记录每个赛季使用的地图集合（多对多关系），`(season_id, map_id)` 唯一索引。

### 地图池与对局地图的一致性校验（V1.3新增）

采集到对局地图后：

1. 在 `map_translation` 中查找该地图，若找不到，按第五章流程处理（`map_not_found`）。
2. 若 `map_translation` 中存在该地图，但该地图不在该比赛所属赛季的 `season_maps` 中：
   * 系统自动将该地图加入 `season_maps`（视为"赛季中途新增地图"），**并**写入 `data_issues`（`issue_type = map_pool_mismatch`，状态默认为 `open`），供管理员确认该地图是否确实属于本赛季地图池（避免误加）。

### 作用

支持地图使用率统计、地图胜率统计、赛季地图分析（区分当前赛季地图与历史赛季地图）。

---

# 八、数据库设计（最终字段汇总）

## 8.1 matches（比赛表）

```sql
id              -- 主键
match_date      -- 比赛日期
wr_id           -- 文章ID，唯一索引
title           -- 团战名称
prize_money     -- 当日总奖金
source_url      -- 原始链接
season_id       -- FK -> seasons.id，可为空（season_not_found时）
created_at
updated_at
```

## 8.2 match_details（对战记录表）

```sql
id
match_id        -- FK -> matches.id
game_no
player_a_id     -- FK -> players.id
player_b_id     -- FK -> players.id
score           -- 如 "1:0"，权威字段
winner_id       -- 由 score + player_a_id/player_b_id 程序推导写入并校验
map_id          -- FK -> map_translation.id
created_at
updated_at
```

唯一索引：`(match_id, game_no)`

> 说明：`loser_id` 不单独存储，统计层按需推导。`score` 为权威字段，`winner_id` 仅作冗余便于查询，写入时如与`score`推导结果冲突，记录至`data_issues`（`score_conflict`）。

## 8.3 raw_articles（原始网页存档）

```sql
id
wr_id           -- 唯一索引
source_url
title
html_content    -- 存储方式（是否压缩）开发阶段确定
parsed_status   -- pending / success / failed
parse_attempt_count
created_at
updated_at
```

## 8.4 players（选手表）

```sql
id              -- 内部主键
player_uid      -- 对外稳定标识，如 P000001，唯一索引，创建后不可变
kr_name         -- 当前韩文ID
cn_name         -- 当前确认中文译名
race            -- 种族
current_team_id -- FK -> teams.id
translation_status -- pending / confirmed
created_at
updated_at
```

## 8.5 player_aliases（选手曾用ID表）

```sql
id
player_id       -- FK -> players.id
kr_name_alias   -- 曾用韩文ID
cn_name_alias   -- 对应历史译名（可为空）
created_at
```

## 8.6 player_team_history（选手转队历史）

```sql
id
player_id       -- FK -> players.id
team_id         -- FK -> teams.id
effective_date  -- 该归属生效日期
created_at
```

## 8.7 teams（队伍表）

```sql
id
name_kr
name_cn
created_at
updated_at
```

## 8.8 team_scores（队伍积分/奖金历史）

> V1.1中曾标记为"是否需要"待确认，V1.2最终数据库结构已纳入，V1.3确认保留，用于队伍页"历史战绩/积分趋势"展示。

```sql
id
team_id         -- FK -> teams.id
match_id        -- FK -> matches.id
score           -- 当场比赛后的队伍积分
prize_money     -- 当场比赛队伍获得奖金
created_at
```

## 8.9 seasons（赛季表）

```sql
id
season_name
start_date
end_date
created_at
updated_at
```

## 8.10 season_maps（赛季地图池）

```sql
id
season_id       -- FK -> seasons.id
map_id          -- FK -> map_translation.id
created_at
```

唯一索引：`(season_id, map_id)`

## 8.11 map_translation（地图翻译字典）

```sql
id
name_kr
name_cn
created_at
updated_at
```

## 8.12 prize_pool（奖金统计表）

```sql
id
match_id        -- FK -> matches.id
player_id       -- FK -> players.id，团队维度奖金可为空，按需扩展team_id
prize_change    -- 本场奖金变动
created_at
```

> 累计奖金由统计层基于 `prize_change` 实时聚合计算，不存储冗余的累计字段。

## 8.13 crawl_log（采集日志表）

```sql
id
wr_id
status          -- success / failed / retry
error_message
attempt_no
created_at
```

## 8.14 data_issues（数据质量中心）

```sql
id
issue_type      -- 见下方枚举
source_table
source_id
description
status          -- open / in_progress / resolved / ignored
resolution_note -- 处理说明（人工填写）
created_at
updated_at
```

### issue_type 枚举（V1.3更新）

```text
translation_error    -- 翻译相关问题
player_not_found     -- 选手匹配失败
map_not_found        -- 地图翻译字典中找不到
score_conflict       -- 比分/胜者推导冲突
prize_error          -- 奖金数据异常
crawl_error          -- 采集层失败（网络/页面不可达）
parse_error          -- 解析层失败（页面结构异常等，V1.3新增）
season_not_found     -- 比赛日期无法匹配唯一赛季（V1.3新增）
map_pool_mismatch    -- 地图不在赛季地图池中，已自动补充待确认（V1.3新增）
```

---

# 九、数据质量中心（处理流程）

后台新增"数据异常中心"模块，支持：

* 按 `issue_type`、`status` 筛选查看异常列表。
* 点击异常记录可跳转至对应业务模块（如 `score_conflict` 跳转至该场对局的编辑页面）进行人工修正——数据质量中心本身**不直接编辑业务字段**，仅作为问题清单与导航入口，避免与各业务模块的编辑逻辑重复。
* 修正完成后，管理员手动将 `status` 更新为 `resolved`，并填写 `resolution_note`。
* 对于 `crawl_error`/`parse_error` 类型，提供"重新解析"按钮，基于 `raw_articles.html_content` 重新执行解析流程（遵循第4.3节的字段覆盖规则）；解析成功后该异常自动标记为 `resolved`。
* `status = ignored` 用于"确认无需处理"的情况（如确实是网站临时抖动导致的一次性失败）。

---

# 十、统计分析需求（统计口径定义）

## 10.1 选手总战绩

```text
姓名 / 总胜场 / 总负场 / 胜率（保留1位小数，四舍五入）
```

胜率 = 胜场 / (胜场 + 负场)，仅统计已正常完成的对局（异常/弃赛对局是否计入见第十六章待确认事项）。

## 10.2 地图胜率

```text
选手 / 地图（关联map_translation展示中文名） / 胜场 / 负场 / 胜率
```

## 10.3 对阵关系

```text
总战绩 / 近10场（按match_details.created_at倒序取前10条，跨比赛日合并计算） / 地图分布
```

## 10.4 奖金排行榜

```text
排名 / 选手 / 累计奖金（基于prize_pool.prize_change求和）
```

## 10.5 连胜排行

统计维度为**单场对局**，按时间顺序计算，跨团战、跨比赛日均视为连续，直到出现一场失利为止。

```text
最长连胜（历史最高纪录） / 当前连胜（截至最近一场对局）
```

## 10.6 V1.2新增统计项口径定义（V1.3补充）

| 展示项 | 口径定义 |
| ---- | ---- |
| 首页"近期状态榜" | 按选手近10场对局胜率排名（与10.3的"近10场"窗口一致），仅统计近30天内有出场记录的选手 |
| 队伍页"近期状态" | 该队伍全体在役选手近10场对局的合计胜率，按队伍整体排序 |
| 地图页"种族胜率" | 按种族对位（PvT/PvZ/TvZ/同种族对决）分别统计该地图上的胜率，而非单一种族整体胜率 |
| 选手页"奖金趋势" | 按赛季（season_id）为时间轴汇总该选手每个赛季的累计奖金，用于趋势图展示 |
| 选手页"历史所属队伍" | 基于 `player_team_history`，按 `effective_date` 排序展示 |
| 地图页"使用次数" | 该地图在 `match_details` 中出现的对局总数，可按赛季筛选 |

---

# 十一、Web管理后台

## 11.1 权限管理（延续V1.1）

* 后台需登录认证，至少区分两类角色：
  * **管理员**：所有操作权限，包括翻译规则上传、手动重新采集、历史数据导入、赛季/地图池配置、选手合并。
  * **运营/编辑**：可编辑选手译名、种族、队伍归属，处理数据异常中心问题，但不可触发采集、历史数据导入或修改系统配置。
* 关键操作（手动重新采集、历史数据全量导入、翻译规则上传、译名批量修改、选手合并）需记录操作日志（操作人、时间、内容）。

## 11.2 首页

```text
今日比赛 / 最新奖金 / 最新更新日期 / 最近一次采集状态（成功/失败/重试中） / 待处理数据异常数量
```

## 11.3 比赛管理

支持查看比赛列表（含wr_id、采集状态、赛季归属）、查看详情、手动重新采集（需权限校验）。

## 11.4 选手管理

支持查看选手、编辑译名（触发translation_status变更流程）、编辑种族/当前队伍（写入player_team_history）、选手合并（处理重复选手记录，流程见第十六章）。

## 11.5 翻译规则管理

支持上传 `translate_rules.md`（自动重新加载）、查看待确认翻译列表、维护 `map_translation` 字典表。

## 11.6 赛季与地图池管理（V1.2/V1.3）

支持新增/编辑赛季（名称、起止日期）、维护赛季地图池（`season_maps`）、处理 `season_not_found`/`map_pool_mismatch` 类异常。

## 11.7 历史数据导入（V1.2）

支持指定wr_id范围或日期范围进行全量重新导入，导入前展示预计影响范围（涉及多少篇文章），导入后展示结果摘要（成功/失败/冲突数量）。

## 11.8 数据异常中心（V1.2/V1.3）

见第九章。

---

# 十二、前台数据统计网页

## 12.1 首页

```text
最新团战结果 / 今日奖金变化 / 最近10场比赛 / 奖金排行榜 / 连胜排行榜 / 近期状态榜
```

## 12.2 选手页

```text
头像（来源待确认，见第十六章） / 中文名 / 韩文名 / 种族 / 当前所属队伍
总战绩 / 地图胜率 / 种族胜率 / 历史所属队伍 / 历史战绩 / 奖金趋势 / 最近20场比赛
```

## 12.3 对阵分析页

例如 `Flash VS SoulKey`，显示历史交手、胜率、地图分布、最近状态。

## 12.4 地图页（V1.2新增）

```text
地图中文名 / 地图韩文名 / 所属赛季 / 使用次数 / 种族胜率
```

## 12.5 队伍页（V1.2新增）

```text
队伍成员 / 累计奖金 / 历史战绩 / 近期状态
```

## 12.6 奖金榜

实时排行榜，基于 `prize_pool` 聚合。

---

# 十三、自动任务与告警

## 13.1 调度

采用Cron，执行时间：每天10:00（时区说明见第十五章）。

## 13.2 流程

```text
检查新文章（支持批量补抓）
↓
保存原始HTML（raw_articles）
↓
采集解析
↓
赛季归属判定 + 地图池校验
↓
翻译（含改名场景与AI待确认标记）
↓
入库（含winner_id校验，按4.3节幂等规则upsert）
↓
刷新统计
↓
记录日志（crawl_log）
↓
告警判断
```

## 13.3 告警机制（延续V1.1）

* 若单篇文章采集连续3次重试均失败，触发告警通知（渠道见第十六章待确认）。
* 若翻译模块"待确认"译名堆积超过阈值，定期提醒管理员。
* 若 `data_issues` 中 `open` 状态记录数超过阈值，定期提醒管理员处理（V1.3新增，避免赛季/地图池异常积压）。

---

# 十四、异常处理

## 14.1 网站无法访问

记录至 `crawl_log`，状态 `failed`，自动重试3次，超过仍失败则触发告警。

## 14.2 解析失败

按4.2节流程，写入 `raw_articles`（`parsed_status = failed`）及 `data_issues`（`parse_error`），不创建对应 `matches` 记录。

## 14.3 翻译失败

入库时使用原韩文，`translation_status = pending`，等待人工修正，不阻塞整体采集流程。

## 14.4 数据重复

`matches` 按 `wr_id` 唯一索引、`match_details` 按 `(match_id, game_no)` 唯一索引去重，全量重新导入遵循4.3节upsert规则。

## 14.5 对战数据字段冲突

`score` 与推导出的 `winner_id` 不一致时，写入 `data_issues`（`score_conflict`），标记为待人工核对，不自动写入正式统计。

---

# 十五、技术架构建议

## 15.1 后端

```text
Python 3.12
FastAPI
SQLAlchemy
APScheduler
```

## 15.2 数据库

```text
PostgreSQL 16
```

每日自动备份，保留至少30天（具体周期待确认，见第十六章）。

## 15.3 前端

```text
Vue3
Element Plus
ECharts
```

## 15.4 部署

```text
Docker
Nginx
PostgreSQL
FastAPI
Vue3
```

服务器IP、域名等部署信息记录于独立《部署配置文档》，不写入本PRD正文。

## 15.5 时区设置

* ELOBOARD发布时间基准为KST（与北京时间相同，UTC+8）。
* 数据库统一使用UTC存储时间戳，应用层按KST展示，避免`match_date`出现"差一天"问题。
* 采集任务"每天10:00"的具体时区在部署配置中明确（建议服务器统一设为UTC+8，与KST对齐，简化逻辑）。

---

# 十六、待确认事项清单（V1.3更新版）

### 已在V1.2/V1.3中解决（仅作记录）

* ~~队伍积分历史是否需要~~ → 已确认需要，新增`team_scores`表。
* ~~历史数据首次导入~~ → 已通过"历史数据回补机制"解决。
* ~~选手改名后历史数据如何保持一致~~ → 已通过`player_uid`+`player_aliases`+`player_team_history`解决。

### 仍需产品/运营方明确

1. 异常/弃赛对局是否计入总战绩与连胜统计？如计入，比分如何标注？
2. 数据库备份保留周期及存储位置（本机/云存储）。
3. 告警通知渠道（邮件/Telegram/企业微信等）及接收人。
4. 译名确认后是否需要同步写回`translate_rules.md`文件，还是仅数据库维护？
5. 选手改名后，历史比赛记录的展示名是否应保留"当时译名"，还是统一展示"当前最新译名"？（当前方案为后者，见5.2节）
6. 选手头像数据来源（ELOBOARD抓取 / 运营手动上传 / 暂不支持）。
7. "近10场""近期状态"等统计窗口是否需要支持前台自定义切换（如近5场/近20场）。
8. 列表补抓"N篇"默认值（默认10）是否合理；首次部署历史回溯的起始wr_id范围。
9. "选手合并"功能的具体交互流程（如何选择主记录、`player_uid`保留规则、历史数据迁移方式）。
10. `raw_articles.html_content`是否需要压缩存储或仅保留关键DOM片段。

---

# 十七、未来扩展规划（独立评估，非本版本范围）

V1.2已明确移除AI战报、微信公众号推送相关需求。以下内容如未来有需要，建议作为独立项目/版本另行立项评估，本PRD不预留相关字段：

## 17.1 星际争霸预测系统

基于历史交手（`match_details`）、地图胜率（10.2）、最近状态（10.6）等数据，预测对局胜率。该功能对现有数据结构无破坏性需求，理论上可在现有表基础上扩展，不影响V1.3的实施。

## 17.2 AI赛事分析 / 公众号联动（已移除）

如未来重新评估，需另行设计数据表（如战报记录表、推送任务表），不在V1.3数据库结构中预留。

---

# 十八、最终数据库结构总览

```text
matches
match_details

raw_articles

players
player_aliases
player_team_history

teams
team_scores

seasons
season_maps

map_translation

prize_pool

crawl_log
data_issues
```

---

# 十九、项目最终目标

构建一个长期稳定运行的韩国星际争霸职业团战数据平台，实现：

```text
自动采集（含原始存档与历史回补）
    ↓
自动翻译（含改名/AI待确认机制）
    ↓
自动统计（明确口径，含赛季/地图池维度）
    ↓
数据分析（数据质量中心持续治理）
    ↓
网页展示
```

具备权限管理、备份、告警、数据质量治理等基础运维保障，支持历史数据积累、赛季管理、地图分析、选手统计、奖金统计，并为未来预测系统扩展预留空间。
