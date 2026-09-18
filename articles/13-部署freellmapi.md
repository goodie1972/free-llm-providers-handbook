# 手把手：在免费云上把 freellmapi 跑起来（聚合你的免费额度）

> 时效声明：本文部署命令基于 **2026-09-15** 核对的 freellmapi 官方文档（`freellmapi.co/install.sh` + GitHub README）。具体镜像名、端口、面板路径以你执行时的官网为准。三丰云等面板操作因各家 UI 不同，只给通用思路，以你实际后台为准。

## 一、为什么单独写部署

前面 12 篇把"聚合 / 路由 / 压缩"三家概念掰扯清了，也说了 freellmapi 是"把你的免费 key 堆成规模"的原教旨白嫖党神器。但 12 篇止于"它是什么"，这篇进"**怎么真的跑起来**"。

因为"能调模型"和"跑得稳"中间，差的就是一次部署。你手上攒了 Google AI Studio、Groq、Mistral、Cerebras 一堆免费 key，散着用累，freellmapi 把它们聚到一个 `/v1` 后面，给编码工具一个统一端点——这事儿值得动手做一次。

我自己的判断：**免费云 + 一行脚本，是个人玩家成本最低的解法**。下面是照着能走的流程。

---

## 二、先说清楚它跑起来长啥样

部署完，你本地/服务器上会有一个服务：
- 监听 `http://<你的地址>:3001`；
- 后台 `Keys` 页：你填各家免费 key（Google / Groq / Mistral / Cerebras…），它统一加密存本地（AES-256-GCM）；
- 它给你一个 `freellmapi-` 开头的**统一 key**；
- 你的客户端（OpenCode / Cline / Cursor）只配这一个 `base_url` + 这一个 key，背后的 provider 随便换；
- `model="auto"` 让它的路由器自己挑；还能 `auto:fast` / `auto:smart` 偏速度或能力。

关键点：**它甚至实现了 Anthropic 的 `/v1/messages` 格式**，所以 Claude Code 也能接这个网关走免费池子。这是它比纯 OpenAI 格式网关多的一块料。

---

## 三、方案 A：本机一行脚本（最快，先跑通）

如果你只是自己用、机器常开，本机最直接：

```bash
curl -fsSL https://freellmapi.co/install.sh | bash
```

脚本会：建 `~/freellmapi` 目录 → 生成加密密钥 → 拉镜像 → 起容器。然后开 `http://localhost:3001` 就是后台。

上手 3 步：
1. 浏览器开 `http://localhost:3001`，进 `Keys` 页；
2. 把你的各家免费 key 填进去（Groq 的 `gsk-`、Google AI Studio 的 `AIza`、Mistral 的 `api_`…）；
3. 生成一个 `freellmapi-` 统一 key，复制到你的客户端：

```python
from openai import OpenAI
client = OpenAI(
    base_url="http://localhost:3001/v1",
    api_key="freellmapi-your-unified-key",
)
resp = client.chat.completions.create(
    model="auto",
    messages=[{"role": "user", "content": "你好"}],
)
print(resp.choices[0].message.content)
```

跑通这一下，你就有了"一个端点管所有免费 key"的底座。本机方案适合开发机常开的人，缺点是机器关了服务就停。

---

## 四、方案 B：免费云常驻（推荐个人玩家）

想要"24 小时在、手机也能调"，就丢到一台免费云上常驻。以**三丰云**（你之前有部署计划）这类免费云为例，通用思路如下，具体按钮以你后台 UI 为准：

**第 1 步：开一台免费云主机**
- 在面板新建实例（系统选 Ubuntu 22.04 这类带 Docker 的）；
- 记下分配的公网 IP；
- 安全组/防火墙放行 `3001` 端口（TCP 入站）。

**第 2 步：装 Docker + 跑安装脚本**
SSH 进机器，先确保有 Docker，然后跑同一行脚本：
```bash
# 若没 Docker，先装（以 Ubuntu 为例，具体看云镜像）
curl -fsSL https://get.docker.com | bash
# 再跑 freellmapi 安装
curl -fsSL https://freellmapi.co/install.sh | bash
```
脚本会起容器监听 `0.0.0.0:3001`。

**第 3 步：反向代理 + HTTPS（重要）**
裸 `http://IP:3001` 在外网跑有两个问题：① 你的 key 明文传；② 容易被扫。正经做法是在前面怼一层反代（Caddy / Nginx）加 HTTPS：
- Caddy 配一段 `your-domain.com { reverse_proxy localhost:3001 }`，自动签证书；
- 域名用你自己的，别用默认 IP 直连。

**第 4 步：登录后台填 key**
开 `https://your-domain.com`，进 `Keys` 页填各家免费 key，拿统一 key 给客户端用（base_url 改成你的域名）。

> 三丰云面板的具体按钮名（"实例/容器/安全组"）各家不同，照"建主机→开端口→SSH→跑脚本→反代"这个骨架走即可，卡在某一步把面板截图发我，我帮你对。

---

## 五、把它当 provider 池喂给 9router（进阶玩法）

12 篇说过，freellmapi（端口 3001）和 9router（端口 20128）不冲突，可以串起来：**freellmapi 当免费额度池，9router 当编码时的智能路由 + RTK 压 token**。

也就是：客户端 → 9router(`localhost:20128`) → freellmapi(`localhost:3001`) → 各家免费 key。纯免费闭环，编码永不断线、token 还省。这是我本地实际在跑的组合。

---

## 六、部署必踩的 4 个坑

**坑 1：默认没 HTTPS，key 裸奔。**
外网裸 `http` 跑等于把统一 key 摊给全网。务必反代 + HTTPS（第四节第 3 步），别省。

**坑 2：防火墙忘了开 3001。**
云上起完容器发现连不上，十有八九是安全组没放行端口。先查这个再查别的。

**坑 3：免费 key 本身会过期/限流。**
freellmapi 不生产额度，它只是聚合你的 key。某家 key 失效了，它那条通道就空了——定期回 `Keys` 页续/换 key。这也是为什么它需要你"管"，不是一劳永逸。

**坑 4：它自己写"仅限个人实验，非生产"。**
项目 README 第一段就标了。真要上生产，底下接付费 provider 兜底，别让免费层扛 SLA（这条和 12、18 篇的纪律一致）。

---

## 七、验证部署成功

起完服务，用一行 curl 验它真活了：
```bash
curl -X POST https://your-domain.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer freellmapi-your-unified-key" \
  -d '{"model":"auto","messages":[{"role":"user","content":"ping"}]}'
```
能正常返回内容，部署就成了。

---

## 系列导航

| 篇目 | 主题 |
|---|---|
| 01 | 开篇：免费 LLM 到底能薅到什么程度 |
| 02 | 国内两入口：魔搭送算力、硅基送额度 |
| 03 | 国内小众免费站实测 |
| 04 | 国内篇实战工作流 |
| 05 | 国外免费大盘点（Gemini / Mistral / Groq / HuggingFace） |
| 06 | Groq 与 OpenRouter 实测 |
| 07 | NVIDIA 与 OpenRouter 对比 |
| 08 | 国外「云+编码」免费档（AMD / Ollama 云 / opencode） |
| 09 | 国外小众免费站踩坑（Peezy / OrcaRouter / B.AI） |
| 10 | unorouter 专篇（一个 key 打通 190+ 免费模型） |
| 11 | 国内如何用上国外免费（合规 + 可用方案） |
| 12 | 聚合代理原理与选型（freellmapi / One API / 9router / omniroute / bifrost） |
| **13** | **← 本篇：手把手在免费云部署 freellmapi** |
| 14 | （预告）多 Key 管理与负载均衡：One API 视角 + freellmapi Fallback |

---

## 结尾：一句真心的

freellmapi 的部署，难的是"第一次动手"而不是"步骤多"。一行脚本 + 一个反代，半小时就能有一个常驻的免费额度池。我自己的建议：**先本机方案 A 跑通，确认体感对了，再丢免费云做常驻**——别一上来就折腾服务器，跑通才是第一性。

下一篇（14）我讲"多 Key 管理 + 负载均衡"：当你 key 多了、channel 多了，怎么用 One API 做分发闸门、怎么给 freellmapi 配 Fallback Chain，让一个挂了自动切下一个。聚合的下一步，是"管得稳"。
