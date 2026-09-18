# unorouter 专篇：一个 key 打通 190+ 免费模型，我的「免费聚合」新宠

> 时效声明：本文数据核实于 **2026-09-15**。unorouter 的模型数和免费池每天随上游浮动（我搜到 190、219、234、324 几种口径），文里那些"覆盖多少家、多少模型"的数字都是某一天的快照，你看到时以官网 `unorouter.com/models` 实时页面为准。

## 一、为什么我要单开一篇写它

前面 05 到 09，我把国外能白嫖的额度盘了一圈：Gemini、Mistral、Groq、HuggingFace、NVIDIA、OpenRouter 的免费层……但你只要真用起来就会发现一个别扭事——**每家一个端点、一个 key、一套限流规则**。

Claude Code 里配一个 `base_url`，Cursor 里又配一个，Codex 再来一个；想换模型就得改代码；某一家的免费层被限流了，工作流直接断在半路。这事儿烦到一定程度，你就不再想"再多薅一家"，而是想"**把这些破 key 统一管起来**"。

这正是聚合网关存在的意义。但聚合网关我也分过类：freellmapi 是把你的免费 key 聚起来（07 那篇提过思路），One API 是运营级分发（13 篇会讲）。而 **unorouter 走的是另一条路——它自己就是一个"免费模型批发市场"**：你不用攒十几个 key，注册拿一个 key，背后直接挂 190+ 个免费模型，自动帮你路由、故障转移。

它最戳我的点就一句：**纯免费优先、OpenAI 格式、一个 key 全搞定**。这对只想"零成本跑通"的个人玩家来说，比自己去攒 key 省太多心。所以单独开一篇，把它的真实用法和坑讲透。

---

## 二、一句话定位

**unorouter = 一个 OpenAI 兼容端点 + 一个 key，背后聚合 190+ 免费模型、47–49 家上游，自动故障转移，无需信用卡。**

它不是"帮你管你自己的 key"（那是 freellmapi/One API 的活），它是"**把自己的免费池子直接喂给你**"。你注册，它给你一个 `sk-` 开头的统一 key，从此只认 `https://api.unorouter.com/v1` 这一个端点。

---

## 三、免费额度速查卡（8 字段）

| 字段 | 内容 |
|---|---|
| ★ 一句话定位 | 纯免费优先的 OpenAI 兼容聚合网关，一个 key 打通 190+ 免费模型 |
| 免费模型数 | **190–234 个**（不同来源口径不一，官网实时 `unorouter.com/models` 为准；付费模型另有 79–90 个） |
| 上游提供商 | 47–49 家（OpenAI / Anthropic / Google / Mistral / DeepSeek / Meta / NVIDIA / 阿里云 等） |
| 免费层限流 | 官方博客称约 **1 请求/分钟/模型/用户**，触发返回 HTTP 429 + `Retry-After`；免费池整体有周额度（具体数字未公开） |
| 协议格式 | **完全 OpenAI 兼容**（`/v1/chat/completions`），现有代码零改动切换 |
| 注册方式 | Discord / GitHub / Email，**无需信用卡** |
| 统一端点 | `https://api.unorouter.com/v1` |
| 邀请/福利 | 注册邀请链接带 `?aff=8j6H`（详见文末「读者福利」） |

> 一个关键机制：免费模型名都带 `:free` 后缀（比如 `glm-5.3-flash:free`、`agnes-2.0-flash:free`）。调的时候写 `model: "xxx:free"` 就走免费池，不带后缀默认走付费。

---

## 四、上手 3 步（直接抄）

### 第 1 步：注册拿 key
进 `unorouter.com`，用 Discord 或 GitHub 一键登录（也可以邮箱），一分钟搞定，**不用绑卡**。在后台生成 API Key，形如 `sk-xxxxxxxx`。

### 第 2 步：把端点指过去
它完全兼容 OpenAI 格式，所以任何现成客户端改个 `base_url` 和 `api_key` 就行。

curl 版：
```bash
curl -X POST https://api.unorouter.com/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 你的_UNOROUTER_API_KEY" \
  -d '{
    "model": "glm-5.3-flash:free",
    "messages": [{"role": "user", "content": "用一句话解释什么是 token 路由"}],
    "stream": true
  }'
```

Python 版（你现有代码几乎不用改）：
```python
from openai import OpenAI

client = OpenAI(
    api_key="你的_UNOROUTER_API_KEY",
    base_url="https://api.unorouter.com/v1",
)
resp = client.chat.completions.create(
    model="glm-5.3-flash:free",
    messages=[{"role": "user", "content": "帮我写个快速排序"}],
)
print(resp.choices[0].message.content)
```

### 第 3 步：接进你的工具
因为格式兼容，下面这些工具都是"改 base_url"的 drop-in 玩法，官方都有对应接入指南：
- **编码 Agent**：OpenCode、Cline、Roo Code、Kilo Code、Zed（把它们的 provider 设成 custom OpenAI，指 `api.unorouter.com/v1` 即可）；
- **角色/小说客户端**：SillyTavern、Janitor.AI、Chub、RisuAI（支持 SillyTavern 卡导入、人设/ Lorebook / 群聊）；
- **CLI 工具**：Aider、Codex、Gemini CLI、OpenClaw。

我自己的用法：把编码工具（OpenCode）的 base_url 指过去，平时调 `:free` 模型写小脚本、跑 agentic loop，一分钱不花就能把工作流跑通——这正是我前面说的"别让限流打断心流"的免费解法之一。

---

## 五、它到底香在哪（我梳理完的真实亮点）

**1. 免费池是真·大。** 190+ 免费模型挂在同一个端点后面，涵盖智谱 GLM、DeepSeek、Qwen、Llama、Mistral、NVIDIA Nemotron、MiniMax、Agnes 等一票主流和社区微调。你想换模型，改个 `model` 字段就行，不用再去十几个平台分别注册。

**2. 自动故障转移，不是"壳"。** 官方博客明确写了：如果一个模型的某家上游限流了，请求会返回显式的 `HTTP 503 + "all providers busy"`，然后后台 health cron 几分钟内把该通道重新探活、重新启用。意思是——**多源免费模型在任意一家上游耗尽后还能接着答**，不像单源免费模型那样一家挂就全 stall。这点比"纯中转"靠谱。

**3. 自带角色聊天客户端，且偏隐私。** 官网内置一个浏览器聊天界面，免费模型已经接好，**不用注册、不用 key、打开就能聊**；支持人设、预设、Lorebook、群聊、swipe，还能导入 SillyTavern 卡。关键：对话存在你浏览器本地，不上服务器；还支持 **BYOK**（自带你自己的 OpenAI 兼容端点 + key，直接从浏览器发）。对非技术用户，这是"不想配环境也能用"的入口。

**4. 编码栈友好。** 它对 OpenCode / Cline / Roo / Zed 这些 AI 编程工具有专门接入指南，base_url 一指就行。配合前面说的"免费池 + failover"，编码 agent 的"429 打断心流"问题能缓解一大半。

**5. 定位对标 OpenRouter 免费层，但更"免费优先"。** OpenRouter 的 `openrouter/free` 是随机路由、模型不固定；unorouter 是"我自建一个 190+ 免费池"，你点名要哪个 `:free` 模型就能要到哪个，可控性更强。

---

## 六、踩坑 3 条（我替你先踩了）

**坑 1：限流是真严，别当生产用。**
官方博客自己说约 1 请求/分钟/模型。190+ 模型的好处是"这家满了换那家"，但你**不能指望同一模型高频调用**。多用户并发、批量任务基本别想。心智模型：它适合个人调试、原型验证、agentic loop 低频试探，不适合"服务别人"。

**坑 2：免费池数字天天浮动，别当承诺。**
我搜到 190、219、234、324 几种模型总数口径——因为上游免费池随时被抽干又恢复。今天写"234 个免费"，你看到时可能变。文章里所有数字都以"官网实时为准"理解，别拿本文当长期合同。

**坑 3：付费模型和免费模型混在一个端点，别调错。**
端点后面既有免费也有付费（79–90 个），**不带 `:free` 后缀的模型默认走付费、消耗信用卡额度**。新手最容易犯的错：抄了个模型名没带 `:free`，跑着跑着发现扣费了。铁律——免费用途，模型名务必带 `:free`。

**替代方案**：如果你想要"管自己攒的 key"而不是用它家的免费池，回头看 freellmapi（把你的 Groq/硅基 key 聚起来）；如果你要管团队、做计费分发，那是 One API 的活（13 篇讲）。unorouter 的优势是"零配置直接白嫖"，劣势是"池子不是你的、限流你控制不了"。

---

## 七、适合谁 / 不适合谁

**✅ 适合谁**
- 不想注册十几个平台、就想"一个 key 跑通"的个人玩家；
- 用 OpenCode / Cline / SillyTavern 这类 OpenAI 兼容工具、想零成本接模型的人；
- 做原型验证、agentic loop 试探、学 AI 开发的学生/独立开发者；
- 想要"打开网页就能聊、不用注册"的轻量角色聊天用户（内置客户端）。

**❌ 不适合谁**
- 要高频并发、服务多用户的生产场景（限流 1/min 直接劝退）；
- 对模型品牌/输出稳定性极其敏感、不能接受池子浮动的场景；
- 想完全自控 key、数据不出自有机房的（它的免费池在它家服务端，BYOK 才能把请求发你自己端点）；
- 需要前沿闭源旗舰（Claude Opus / GPT-5 那批在付费层，不在免费池）。

---

## 八、和 OpenRouter 免费层怎么选

这是被问最多的问题，我直接给结论：

| 维度 | unorouter 免费池 | OpenRouter `openrouter/free` |
|---|---|---|
| 模型可控性 | 点名要哪个 `:free` 模型 | 路由随机分配，不保证同一模型 |
| 免费模型数 | 190+（自建池） | 19+（随机路由池） |
| 故障转移 | 显式 503 + 自动重探活 | 路由层兜底 |
| 接入成本 | 一个 key 直接白嫖 | 一个 key 直接白嫖 |
| 适合 | 想点名模型、免费优先 | 不挑模型、能用就行 |

一句话：**想要"点名要某个免费模型 + 池子大"，选 unorouter；只要"能答、不挑谁答"，OpenRouter 免费路由也够**。两者不冲突，我本地都留着，按当时手感切。

---

## 九、读者福利（邀请小框）

unorouter 有邀请机制，用这个链接注册双方可能有奖励（以官网实时政策为准）：
`unorouter.com/register?aff=8j6H`

> ⚠️ disclaimer：邀请政策、额度随时可能调，码有效性以你注册时官网显示为准；本文不保证该码长期有效，失效就用官网默认注册入口。

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
| **10** | **← 本篇：unorouter 专篇（一个 key 打通 190+ 免费模型）** |
| 11 | （预告）国内如何用上国外免费：合规 + 可用方案 |
| 12 | 聚合代理原理与选型（freellmapi / One API / 9router / omniroute / bifrost） |

---

## 结尾：一句真心的

unorouter 让我最舒服的一点，是它把"免费聚合"这件事做到了**零配置**——你不用去攒 key、不用自己搭网关，注册拿一个 key 就能站在 190+ 免费模型的肩膀上。它的天花板也很清楚：限流严、池子不是你的。所以我的用法一直是——**它当日常白嫖底座，真要稳的活儿底下再接一两个付费 provider 兜底**（这和 13 篇要讲的"聚合层别裸奔"是同一个道理）。

下一篇（系列第 11 篇）我会讲一个更落地的问题：**身在国内，怎么合规、可用地用上这些国外免费层**——毕竟"能免"和"用得安心"之间，还差一层姿势。

反正这类网关我现在本地留了好几个镜像，但日常真正在跑的，也就那一两个。你要是也在纠结从哪开始，先把 unorouter 这个 key 申请了、接进你最常用的那个工具，跑通一次，你就懂我说的"零配置白嫖"是什么体感了。
