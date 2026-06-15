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

## 经验总结

| 类别 | 要点 |
|------|------|
| Windows 环境 | PowerShell 5.x 不支持 `&&`、HEREDOC、`$()` 等 Bash 语法 |
| Git 操作 | push 前确认远程仓库已存在；commit message 在 Windows 下保持单行 |
| 工具链 | gh CLI / Docker 需提前安装；未安装时使用替代方案 |
| Edit 工具 | 替换前必须 Read 精确内容；缩进/空格必须完全一致 |
| 代码规范 | 同模块 import 合并；逐步添加时注意代码整洁 |
