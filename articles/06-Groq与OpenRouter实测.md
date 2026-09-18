# 速度怪兽 Groq + OpenRouter 实测

> 上篇《国外免费大盘点》我们盘了 Gemini / Mistral / Groq / HuggingFace 四家"有没有免费"。这一篇不啰嗦，直接上实测：Groq 到底有多快？OpenRouter 的 `:free` 模型怎么用才不踩坑？两者怎么搭进你 04 那套工作流最香？
> 系列定位：本篇是第二辑第 2 篇（模板 A 单 provider 深评），同时拆 Groq 与 OpenRouter 两家——一个拼速度，一个拼"什么都能调"。

## 一、先说结论（懒人版）

- **Groq**：免费档里的速度天花板。自研 LPU 芯片把开源模型跑出 300–800 token/秒，实测 gpt-oss-120b 约 642 tok/s，是典型 GPU 免费接口的 6–10 倍。**适合实时聊天、语音、Agent、批量高速生成**；但不追求"最强模型"，模型是精选开放权重。
- **OpenRouter**：一个 Key、一个 OpenAI 兼容端点，调 400+ 模型。`:free` 后缀模型 $0 token；免费账号 20 RPM / 50 RPD，一次性充 $10 直接升到 1000 RPD。**适合"什么模型都试试"和兜底**。
- **最佳组合**：Groq 跑实时高频，OpenRouter 跑多模型尝试 + Fallback。两者都是 OpenAI 兼容，改两行就能切换。

## 二、Groq 免费层深评 ★

### ★ 一句话定位
Groq 不是模型厂，是**推理厂**——用自研 LPU（Language Processing Unit）芯片，把 Llama、Qwen、DeepSeek、gpt-oss 等开源模型跑出 GPU 做不到的推理速度。免信用卡、永久免费档。

### ★ 免费额度速查卡（8 字段）

| 字段 | 内容 |
|------|------|
| 入口 | console.groq.com（Google / GitHub 登录，无卡） |
| 免费模型 | openai/gpt-oss-120b、gpt-oss-20b、qwen3.6-27b、qwen3.8-27b、groq/compound（含联网） |
| 速率（对话模型） | 30 RPM / 1,000 RPD（按模型独立计，24h 重置） |
| 速率（语音 whisper） | 20 RPM / 2,000 RPD |
| 上下文 | 多数 131K；gpt-oss 系列输出上限为 0（仅 reasoning 用途）需注意 |
| 兼容性 | 完全 OpenAI 兼容（base_url 一改即用） |
| 信用卡 | 不需要 |
| 状态 | 永久免费档，但无 SLA、高峰可能排队 |

### ★ 上手 3 步（可跑代码）
1. 打开 console.groq.com，用 Google 或 GitHub 登录（不用绑卡）。
2. 左侧栏 **API Keys → Create API Key**，复制保存（只显示一次）。
3. 把现有 OpenAI 代码改两行：`base_url` 换成 `https://api.groq.com/openai/v1`，`model` 换成免费模型名。

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key="你的_GROQ_API_KEY",
)

resp = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[{"role": "user", "content": "用一句话解释什么是 LPU"}],
)
print(resp.choices[0].message.content)
```

### ★ 固定基准实测（第三方实测，2026-08）
我们引用第三方在 2026-08 对 gpt-oss-120b 的实测：单条流式请求、temperature 0.3、生成 500 token，吞吐 = 完成 token ÷ 生成耗时（剔除首 token 延迟）≈ **642 tok/s**，落在 Groq 官方 300–800 区间中上。

| 指标 | Groq（gpt-oss-120b） | 典型 GPU 免费接口 | 倍数 |
|------|------|------|------|
| 生成吞吐 | ~642 tok/s | 50–100 tok/s | 6–10× |
| 首 token 延迟 | 受网络距离主导（不具参考性） | 同左 | — |
| 是否需卡 | 否 | 多数否 | — |

> 别只看"首 token 延迟"：那主要看你到美西机房的距离，不是 Groq 硬件。真正能横向比的是**吞吐**——而这一项免费档里 Groq 几乎没对手。

### ★ 适合谁 / 不适合谁
- **适合**：实时对话、语音助手、Agent 工具调用（Groq 工具决策约 600ms vs GPT-4o 1800ms，3× 快）、批量高速生成。
- **不适合**：要最强前沿模型（GPT/Claude 级质量）、要稳定 SLA 的生产环境。

### ★ 踩坑 3 条 + 替代
1. **老教程的 `llama-3.3-70b-versatile` 在自助免费档已下架 / 转 Enterprise（Contact Sales）**，填进去会直接报错。改用 `openai/gpt-oss-120b` 或 `qwen3.x-27b`。网上还在传的"14,400 RPD"多半指极小的 prompt-guard 分类器，不是你能聊天的模型。
2. **速率按模型独立计、每日重置**：小模型（gpt-oss-20b）RPD 更宽松，批量拆到小模型更稳。
3. **免费档无 SLA、高峰可能排队**：真要上生产，要么付费档，要么 Groq + OpenRouter 双活兜底。

## 三、OpenRouter 免费层深评 ★

### ★ 一句话定位
OpenRouter 是**统一网关**：一个 Key、一个 OpenAI 兼容端点，调 400+ 模型。模型 ID 带 `:free` 后缀的就是免费档，token 成本 $0；免费账号 20 RPM / 50 RPD。

### ★ 免费额度速查卡（8 字段）

| 字段 | 内容 |
|------|------|
| 入口 | openrouter.ai（Google / GitHub / 邮箱登录，无卡） |
| 免费模型 | 20+ 个 `:free` 模型，阵容随官网轮换 |
| 速率（免费账号） | 20 RPM / 50 RPD（账号级，全模型共享） |
| 速率（充 $10 后） | 20 RPM / 1,000 RPD（一次性，余额归零仍保留） |
| 上下文 | 免费端点有时比付费版短，长文注意截断 |
| 兼容性 | 完全 OpenAI 兼容 |
| 信用卡 | 免费模型不需要；充 $10 才需支付 |
| 状态 | 永久有免费模型，但阵容常变 |

### ★ 上手 3 步（可跑代码）
1. 打开 openrouter.ai → 登录 → 右上角 **Keys → Create Key**（只显示一次，存好）。
2. 把 `base_url` 换成 `https://openrouter.ai/api/v1`，`model` 换成 `:free` slug。
3. 加 `extra_body` 的 `route: fallback` 做多模型兜底，避免单点挂掉。

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="你的_OPENROUTER_API_KEY",
)

resp = client.chat.completions.create(
    model="z-ai/glm-5.2:free",
    messages=[{"role": "user", "content": "REST 和 GraphQL 有什么区别？"}],
    extra_body={"route": "fallback",
                "models": ["z-ai/glm-5.2:free",
                           "nvidia/nemotron-3-super-120b-a12b:free",
                           "google/gemma-4-31b-it:free"]},
)
print(resp.choices[0].message.content)
```

### ★ 当前热门免费模型（截至 2026-09 核验）
免费阵容会轮换，依赖前先去 openrouter.ai/models 筛选 `Free`。2026-08/09 第三方核验的热门款：

| 模型 ID | 上下文 | 擅长 |
|------|------|------|
| nvidia/nemotron-3-ultra-550b-a55b:free | 1M | 免费档最强推理，长文档/研究 |
| nvidia/nemotron-3-super-120b-a12b:free | 262K | 通用强模型，MoE 高效 |
| cohere/north-mini-code:free | 256K | 编程 Agent |
| google/gemma-4-31b-it:free | 262K | 轻快全能、多语言 |
| openai/gpt-oss-120b:free | 131K | 通用推理 + 工具调用 |
| z-ai/glm-5.2:free | 256K | 旗舰级免费全能 |
| openrouter/free | 200K | 自动挑一个在线的免费模型，永不失效 |

### ★ 适合谁 / 不适合谁
- **适合**：一个 Key 试遍模型、做 Fallback 高可用、原型验证、想用 NVIDIA/Google/OpenAI 开源权重但不想分别注册。
- **不适合**：要稳定低延迟的生产流量；**敏感数据**要小心——部分供应商可能用你的数据训练，OpenRouter 会标数据政策，机密内容请用不训练数据的付费档或本地 Ollama。

### ★ 踩坑 3 条 + 替代
1. **免费阵容会轮换**：DeepSeek、Mistral 当年的热门免费变体都已撤。别把代码写死依赖某一个 `:free`，上线前查实时列表。
2. **失败请求也计入每日配额**：一个写崩的重试循环能把 50 次额度几分钟烧光。务必加退避、加上限。
3. **负余额连免费也报 402**：即使只用 `:free`，账户余额为负也会失败；保持 ≥ $0。

## 四、两者怎么搭进你的工作流（路由示例）
把 04 那套 ROUTER 扩两行，实时/编码走 Groq，多模型尝试 + 兜底走 OpenRouter：

```python
ROUTER = {
    "long_context":  {"base_url": "https://api.siliconflow.cn/v1",  "model": "deepseek-ai/DeepSeek-V3"},
    "coding":        {"base_url": "https://api.groq.com/openai/v1", "model": "openai/gpt-oss-120b"},
    "realtime":      {"base_url": "https://api.groq.com/openai/v1", "model": "qwen/qwen3.8-27b"},
    "tryanything":   {"base_url": "https://openrouter.ai/api/v1",   "model": "openrouter/free"},
    "fallback":      {"base_url": "https://openrouter.ai/api/v1",   "model": "z-ai/glm-5.2:free"},
}
```

> 一句话：Groq 当"发动机"，OpenRouter 当"变速箱 + 备胎"。免费档里这套组合几乎覆盖你能想到的所有场景。

## 五、下一篇预告 & 系列导航
下一篇（07）我们**深度对比 NVIDIA vs OpenRouter**：自营开放权重托管 vs 聚合网关，从免费层形态、模型覆盖、成本透明度到数据合规逐条掰开。

**系列导航**：01 国内 6 大厂横评 → 02 魔搭 / 硅基流动 → 03 国内小众免费站实测 → 04 个人 AI 工作流搭建 → 05 国外免费大盘点 → **06 Groq + OpenRouter 实测** → 07 NVIDIA vs OpenRouter

> 全系列免费额度数据以官网实时为准，本文核验日期 **2026-09-03**。完整可更新版与对照表将同步至 GitHub 仓库（系列收口时开放），欢迎 star 与纠错投稿。
