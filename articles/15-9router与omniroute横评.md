# 智能路由 vs 聚合：9router 与 omniroute 横评，到底选谁

> 时效声明：本文数据基于 **2026-09-15** 核对的 9router / omniroute 公开文档（GitHub README + 官网）。那些"290 家、1.6B token"是项目方自报数字，免费池浮动大，以官网实时为准，别当长期承诺。

## 一、为什么这俩要放一起比

前面 12 篇把聚合/路由/压缩掰扯清了，也提到 9router 和 omniroute **撞了同一个端口（20128）、同一套路（RTK + Caveman + 多层降级）**——它们就是直接竞品，二选一就够，别都装。

但到底选哪个？这俩不是"谁好谁坏"，是"要轻还是要全"。这篇把差异摊开，你照自己口味挑。

先重申它俩解决的痛点（12 篇讲过，复习一遍）：**重度 AI 编码的人，最恨限流打断心流，又想省 token**。它们架在编码工具和各家模型之间，核心三件套——
- **RTK Token 压缩**：请求出 LLM 前，无损压工具输出（git diff、grep、ls、find、tree），典型省 20–40% 输入 token；
- **Caveman Mode**：注入"能少说就少说"系统提示，压输出 token，最高省 65%；
- **多层自动降级**：订阅层（Claude Code/Codex）→ 廉价层（GLM/MiniMax）→ 免费层（Kiro/OpenCode Free/Vertex 额度），一层用完毫秒级切下一层。

---

## 二、9router：轻、专、稳

**一句话**：给"编码永不断线"的人造的路由，干的就是路由+压缩+降级三件事，不多不少。

**怎么跑**（npm 全局装，最省事）：
```bash
npm install -g 9router
9router   # 仪表盘自动开在 http://localhost:20128
```
然后把 Claude Code / Cursor / Cline 的 base_url 指过去。

**最香的点**（灵魂三件套）：
- RTK 压工具输出、Caveman 压输出——agentic loop 里太值钱；
- 三层降级（订阅→廉价→免费），毫秒级切换；
- 双层翻译架构（OpenAI 当中间标准，14 种格式双向互转），连 Claude/Gemini/Cursor 私有协议都能桥；甚至带 MITM 透明代理，能拦 CLI 硬编码的 API 端点。

**最坑的点**：
- 明显偏编码场景，纯聊天用它绕；
- MITM 流量拦截有安全争议（装本地 CA、改 hosts），介意的人不舒服；
- 项目新，踩坑得自己扛。

**适合谁**：重度 AI 编码（Claude Code / Cursor / Codex / Cline）、被限流打断心流、想省 token 的个人。

---

## 三、omniroute：9router 的"堆料全家桶"

**一句话**：和 9router 同一个端口、同一套路，但把数字和功能"堆料"到极致。

**怎么跑**（几乎一样）：
```bash
npm install -g omniroute
omniroute   # 同样 http://localhost:20128
```

**最香的点**（堆料部分）：
- 目录号称 236–290 家提供商、90+ 免费，免费池去重约 1.6B tokens/月；
- **17–18 种路由策略**（priority / cost-optimized / fusion / context-relay 等），比 9router 的"三层"细得多；
- **内置 MCP Server**（95–104 个工具）、A2A 协议、持久记忆（FTS5 + 向量）、guardrails、eval 框架——把 Agent 基础设施也塞进来了；
- 4 层降级（订阅→API key→便宜→免费），切换毫秒级。

**最坑的点**（必须泼冷水）：
- 那些"290 家、1.6B token"是**项目方自报数字**，免费池去重计数虽诚实，但各家上限浮动极大，别当真能稳定薅；
- 项目 2026 年 2 月才起，非常新，生产 benchmark 未必服众；
- **安全默认差**：第一次启动管理员密码是字面量 `CHANGEME`，不手动设 `INITIAL_PASSWORD` 就等于裸奔——这点必须改。

**适合谁**：想要"一个二进制搞定一切、不用自己拼插件"的懒人；编码 + Agent 通吃、愿意尝鲜的人。

---

## 四、横评大表（一眼选）

| 维度 | 9router | omniroute |
|---|---|---|
| 定位 | 编码路由 + 省 token（轻、专） | 编码 + Agent 全家桶（全、新） |
| 默认端口 | 20128 | 20128（冲突，二选一） |
| 核心能力 | 路由 + RTK/Caveman 压缩 + 三层降级 | 路由 + RTK/Caveman 压缩 + 四层降级 + MCP |
| 路由策略 | 三层降级 | 17–18 种 |
| Token 压缩 | ✅ RTK + Caveman | ✅ RTK + Caveman |
| MCP | ❌（仅 Server 思路无内置） | ✅ 内置 MCP Server（95–104 工具） |
| 持久记忆/Agent | ❌ | ✅ FTS5+向量、guardrails、eval |
| 安全默认 | 常规 | ⚠️ `CHANGEME` 裸奔需手动改 |
| 项目年龄 | 较新 | 2026-02 起，极新 |
| 适合 | 要轻、要专、要稳的编码党 | 要全功能、要 MCP、要尝鲜的编码+Agent 党 |

---

## 五、选型结论

**要轻、要专、要稳 → 选 9router。**
它只干路由+压缩+降级，心智负担小，踩坑面窄。纯编码、不想折腾插件的人，闭眼选它。

**要全、要新、要 MCP → 选 omniroute。**
它把路由、压缩、Agent 协议、记忆、eval 全塞进一个二进制，零插件。但代价是：数字更浮、项目更新、安全默认要手动改（记得设 `INITIAL_PASSWORD`）。

**铁律：二选一，别都装。** 端口冲突是小事，配置乱成一锅粥才是大事。我本地留的是 9router——够用、不闹心；你要玩 Agent 基础设施，再换 omniroute。

---

## 系列导航

| 篇目 | 主题 |
|---|---|
| 13 | 手把手部署 freellmapi |
| 14 | 多 Key 管理与负载均衡（One API + freellmapi Fallback） |
| **15** | **← 本篇：9router / omniroute 横评** |
| 16 | （预告）套 Prompt Optimizer 省 token（正面讲你的插件） |

---

## 结尾：一句真心的

这俩兄弟我建议你就记一句：**轻选 9router，全选 omniroute**。它们解决的是"免费额度怎么榨干还不中断"——RTK 压输入、Caveman 压输出、多层降级防 429，这三件套对编码党是真香。

但别忘了 12、14 篇的纪律：免费层再会路由，也没有 SLA。真上生产，底下接付费兜底。下一篇（16）我正面讲一个更上游的省钱法子——**Prompt Optimizer 插件**，从提示词本身砍 token，和路由压缩是两条不同维度的省法。
