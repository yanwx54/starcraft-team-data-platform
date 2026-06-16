# 踩坑日志

韩国星际争霸团战数据自动采集与统计平台

------

## 2026-06-14

### #001 PowerShell 不支持 `&&` 语法

**场景**：在 RunCommand 中使用 `cd "path" && git status` 组合命令。

**现象**：PowerShell 报错 `标记"&&"不是此版本中的有效语句分隔符`。

**原因**：PowerShell 7 之前不支持 `&&` 和 `||` 运算符。Windows 默认的 PowerShell 5.x 不支持。

**解决**：
- 方案一：分开执行命令，不使用 `&&` 连接
- 方案二：改用分号 `;` 连接（但不具备短路逻辑）
- 方案三：安装 PowerShell 7+（支持 `&&`）

**建议**：在 RunCommand 中避免使用 `&&`，改为单独执行每条命令，或使用 `cwd` 参数指定工作目录。

------

### #002 PowerShell 不支持 HEREDOC 语法

**场景**：使用 `git commit -m "$(cat <<'EOF' ... EOF)"` 提交多行 commit message。

**现象**：PowerShell 报错 `Missing file specification after redirection operator` 和 `The '<' operator is reserved for future use`。

**原因**：`<<'EOF'` 是 Bash 的 HEREDOC 语法，PowerShell 完全不支持。`$()` 在 PowerShell 中也有不同含义。

**解决**：改用简单的单行 commit message：
```bash
git commit -m "docs: initial project documentation and configuration"
```

**建议**：在 Windows 环境下，git commit message 保持单行，避免使用 HEREDOC。

------

### #003 GitHub 远程仓库不存在时 push 失败

**场景**：本地 git init 后直接 `git push -u origin master`。

**现象**：报错 `remote: Repository not found. fatal: repository not found`。

**原因**：GitHub 仓库需要先在 GitHub 上创建（网页或 gh CLI），不能仅通过 `git remote add` 自动创建。

**解决**：
1. 在 GitHub 网页手动创建空仓库（不勾选 README/.gitignore/LICENSE）
2. 然后再执行 `git push -u origin master`

**建议**：推送前确认远程仓库已存在。安装 `gh` CLI 可通过命令行自动创建仓库：`gh repo create yanwx54/starcraft-team-data-platform --public`。

------

### #004 `gh` CLI 未安装

**场景**：尝试使用 `gh auth status` 和 `gh repo create` 操作 GitHub。

**现象**：`gh : The term 'gh' is not recognized as the name of a cmdlet`。

**原因**：当前环境未安装 GitHub CLI。

**解决**：手动在 GitHub 网页创建仓库。

**建议**：如需自动化 GitHub 操作，安装 gh CLI：
```powershell
winget install GitHub.cli
gh auth login
```

------

### #005 Docker 未安装导致无法本地验证

**场景**：创建 docker-compose.yml 后执行 `docker compose config` 验证。

**现象**：`docker : The term 'docker' is not recognized`。

**原因**：本地 Windows 开发环境未安装 Docker Desktop。

**解决**：配置文件按规范编写，部署到服务器（Ubuntu 24.04）后验证。

**建议**：
- 本地开发如需容器化，安装 Docker Desktop for Windows
- 或直接在服务器上验证 docker compose 配置

------

### #006 Edit 工具匹配字符串需精确

**场景**：使用 Edit 工具替换 PlayerDetailView.vue 中的 `<!-- 奖金记录 -->` 注释。

**现象**：报错 `String to replace not found in file`。

**原因**：源文件中缩进为 8 个空格（两层缩进），而 old_string 中使用了 6 个空格。Edit 工具要求精确匹配，包括空格和缩进。

**解决**：先用 Read 工具查看目标行的精确内容，再使用完全一致的缩进进行替换。

**建议**：Edit 前务必先 Read 目标区域，复制精确的行内容作为 old_string，避免缩进/空格不匹配。

------

### #007 前端 import 合并优化

**场景**：在 PlayerDetailView.vue 中新增 `getPlayerVsRecord` 和 `getPlayers` 的 import。

**现象**：最初写成两行 import from 同一模块：
```js
import { getPlayerDetail, getPlayerMatches, getPlayerPrizes, getPlayerMapStats, getPlayerVsRecord } from '../api/players'
import { getPlayers } from '../api/players'
```

**原因**：功能逐步添加时未合并同一模块的 import。

**解决**：合并为单行 import：
```js
import { getPlayerDetail, getPlayerMatches, getPlayerPrizes, getPlayerMapStats, getPlayerVsRecord, getPlayers } from '../api/players'
```

**建议**：添加新 import 时检查是否已存在同模块 import，合并而非新增。

------

### #008 Git 忘记提交导致大量变更堆积

**场景**：完成多个 Sprint 后检查 git status，发现大量新增文件和修改未提交。

**现象**：84 个文件未提交，包括整个 backend/ 和 frontend/ 目录。如果此时发生磁盘故障，所有代码将丢失。

**原因**：开发过程中专注于编码，忘记及时 git commit。

**解决**：
1. 每完成一个功能模块后立即 commit
2. 每次会话结束前检查 `git status` 并提交
3. 定期 push 到 GitHub 远程备份

**建议**：养成「完成即提交」的习惯，避免大量未提交变更堆积。可在每次对话结束前主动执行 `git status` 检查。

------

### #009 git upstream 消失警告

**场景**：执行 `git status` 时提示 `Your branch is based on 'origin/master', but the upstream is gone`。

**现象**：本地分支显示跟踪远程分支，但 Git 认为上游已消失。

**原因**：push 后本地远程引用缓存未更新。`git fetch` 后远程分支出现在 `refs/remotes/origin/` 但 `branch --set-upstream-to` 仍报错。

**解决**：
```bash
git fetch origin
git push -u origin master
```
`push -u` 会重新设置跟踪关系。

**建议**：每次 push 后如出现此警告，执行 `git push -u origin master` 即可修复。

------

### #010 Vercel Serverless 不支持持久进程

**场景**：原方案使用 APScheduler 在 FastAPI 容器内定时运行爬虫。

**现象**：Vercel Serverless Functions 是无状态的，每次请求启动新实例，无法运行后台定时任务。

**原因**：Serverless 架构限制 — 没有持久进程，函数执行完毕即销毁。

**解决**：
- 使用 Vercel Cron Jobs 触发 API 端点
- 后端新增 `GET /api/v1/admin/crawler/cron` 端点（CRON_SECRET 鉴权）
- 备用方案：GitHub Actions 定时触发爬虫脚本

**建议**：Serverless 环境下，所有定时任务必须通过外部触发器（Cron / Actions）调用 HTTP 端点。

------

### #011 Vercel Serverless 函数有执行时间限制

**场景**：爬虫一次采集多篇文章，可能耗时较长。

**现象**：Vercel Hobby 计划 Serverless 函数超时限制为 10 秒（Pro 计划 60 秒）。

**原因**：Serverless 函数不适合长时间运行的任务。

**解决**：
- Vercel Cron 端点仅触发后台任务（`BackgroundTasks`），快速返回响应
- 如果采集量大，使用 GitHub Actions 作为主要采集方式（无超时限制）
- 可拆分为单条采集，多次调用

**建议**：爬虫任务优先使用 GitHub Actions，Vercel Cron 作为轻量级补充。

------

### #012 Neon 数据库连接串需要 sslmode=require

**场景**：从 Vercel Serverless 连接 Neon PostgreSQL。

**现象**：连接失败，报 SSL 相关错误。

**原因**：Neon 强制要求 SSL 连接，连接串必须包含 `?sslmode=require`。

**解决**：
```
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/starcraft?sslmode=require
```

**建议**：在 Vercel 环境变量和 GitHub Secrets 中都使用带 `sslmode=require` 的连接串。

------

## 经验总结

| 类别 | 要点 |
|------|------|
| Windows 环境 | PowerShell 5.x 不支持 `&&`、HEREDOC、`$()` 等 Bash 语法 |
| Git 操作 | push 前确认远程仓库已存在；commit message 在 Windows 下保持单行；及时提交避免堆积 |
| 工具链 | gh CLI / Docker 需提前安装；未安装时使用替代方案 |
| Edit 工具 | 替换前必须 Read 精确内容；缩进/空格必须完全一致 |
| 代码规范 | 同模块 import 合并；逐步添加时注意代码整洁 |
| 备份习惯 | 完成功能即提交；会话结束前检查 git status；定期 push 远程 |
| Serverless | 不支持持久进程；函数有超时限制；定时任务需外部触发 |
| Neon | 连接串必须包含 `?sslmode=require` |
