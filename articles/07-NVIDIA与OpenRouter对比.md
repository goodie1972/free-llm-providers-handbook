# NVIDIA vs OpenRouter：自营托管和聚合网关，免费档到底选谁

> 上篇《Groq + OpenRouter 实测》我们聊了「速度怪兽」和「万能网关」。这一篇把对比拉满：NVIDIA NIM（芯片厂直营的开放权重托管）和 OpenRouter（聚合 400+ 模型的网关），同样是「免费」，两家差的不是一点半点。一篇帮你把账算清。

## 一、懒人结论（不想看长文看这句）

- **NVIDIA NIM**：芯片厂自己下场托管开源模型，免费档 **100+ 模型、~40 RPM、不按 token 计费**，还**能自托管**（NIM 容器，API 一模一样）。适合想「在 NVIDIA 地盘上白嫖开源模型 + 未来好迁移到自有机器」的人。
- **OpenRouter**：一个 Key 调 400+ 模型（含 GPT/Claude 前沿），免费档 **20 RPM / 50 RPD**，充 $10 升到 1000 RPD。适合「什么模型都想试、要自动兜底高可用」的人。
- **一句话**：NVIDIA 是「自家厨房随便用」，OpenRouter 是「外卖平台全都有」。免费档要稳、要可自托管选 NVIDIA；要广度、要兜底选 OpenRouter。

## 二、速查总表（NVIDIA vs OpenRouter 八维对比）

| 维度 | NVIDIA NIM | OpenRouter |
| --- | --- | --- |
| 定位 | 自营开放权重托管（芯片厂直营） | 聚合网关（400+ 模型一站式） |
| 免费层形态 | 100+ 开源模型，~40 RPM，无按 token 计费 | 20+ `:free` 模型，20 RPM / 50 RPD（充 $10→1000 RPD） |
| 模型覆盖 | 全开放权重（Nemotron/Llama/DeepSeek/Qwen），无前沿闭源 | 含 GPT/Claude 前沿，但免费档仅开源 |
| 成本透明度 | 免费档真免费；付费 NIM 按 token $0.04–1.20/M | 通过价 + 5.5% 充值费；BYOK +5% |
| 数据合规 | 一手托管，数据落点清晰 | 多一跳网关 + 下游各异；支持 ZDR 路由 |
| 自托管 | 支持（NIM 容器，API 一致） | 不支持（纯托管） |
| 延迟 | 直连 NVIDIA 基础设施，快 | +50–70ms 网关开销 |
| 可复现性 | 模型固定，稳 | 免费路由今日≠明日，需钉死模型名 |

> 下面把上表里最容易踩坑的四维——免费层形态、成本、数据、自托管——逐个掰开。

## 三、逐维掰开

### 1. 免费层形态：一个是「平房随便住」，一个是「按次取号」

NVIDIA 的免费档是**速率限制模式**（2026 年起取消 Credits，改为 RPM）：大多数模型 **~40 RPM**，小模型能到 ~60 RPM，没有每日 token 上限，也没有按 token 计费——纯粹「原型随便跑」。

OpenRouter 的免费档是**双限**：**20 RPM / 50 RPD**（RPD = 每天请求数），失败请求也计入；一次性充 $10，每天额度直接升到 **1000 RPD**。注意它的免费阵容会轮换，别把代码写死依赖某一个 `:free`。

### 2. 成本透明度：NVIDIA 免费就是免费，OpenRouter 有「隐形手续费」

NVIDIA 免费档**零成本**；要上生产就走付费 NIM，按 token 计费（约 $0.04–1.20 / 1M，看模型大小），或下载 NIM 容器自己跑（只付机器钱）。

OpenRouter **不加成模型价**——你付的就是下游 provider 的标价。但它有两笔「平台税」：

- 充值时收 **5.5% 手续费**（最低 $0.80），买 $100 信用实付 $105.50；
- BYOK（自带 Key）走 5% 使用费，且官方页面在「免手续费额度」上自相矛盾（一处写 $25,000/月、一处写 100 万次请求/月），**别把它硬编码进成本预测**。

### 3. 数据合规：NVIDIA 落点单一，OpenRouter 多一跳但有 ZDR

NVIDIA 是**一手托管**，数据只过 NVIDIA 一家，落点清晰，合规审计简单。

OpenRouter 请求会**先过网关、再转给下游 provider**，每层策略不同。好消息是它默认**不记录你的 prompt/completion**（连报错也不记），还提供 **ZDR（零数据留存）路由**——设 `zdr:true` 就只发给标了零留存的后端；不行还能 `data_collection:"deny"` 或拉黑特定 provider。敏感数据用它时，务必显式设路由策略，别假设默认策略覆盖下游。

### 4. 自托管与延迟：要可控选 NVIDIA，要省事选 OpenRouter

NVIDIA 最大杀器是**可自托管**：把 NIM 容器拽到自己 GPU 上跑，API 完全一致，零改代码——未来想脱离云、上自己机器毫无摩擦。

OpenRouter **纯托管、不支持自托管**，这对有 GDPR/HIPAA 强合规要求的团队是硬伤。延迟上，OpenRouter 实测比直连多 **50–70ms** 网关开销；NVIDIA 直连自家基础设施，同模型下更省延迟。

## 四、上手代码（两家都是 OpenAI 兼容）

NVIDIA NIM：

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key="nvapi-你的KEY",
)

resp = client.chat.completions.create(
    model="nvidia/llama-3.3-nemotron-super-49b-v1.5",
    messages=[{"role": "user", "content": "用一句话解释什么是 MoE"}],
)
print(resp.choices[0].message.content)
```

OpenRouter（带自动兜底）：

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="sk-or-你的KEY",
)

resp = client.chat.completions.create(
    model="nvidia/nemotron-3-ultra-550b-a55b:free",
    messages=[{"role": "user", "content": "REST 和 GraphQL 有什么区别？"}],
    extra_body={"route": "fallback",
                "models": ["nvidia/nemotron-3-ultra-550b-a55b:free",
                           "z-ai/glm-5.2:free",
                           "openai/gpt-oss-120b:free"]},
)
print(resp.choices[0].message.content)
```

> 两家注册都不用绑卡：NVIDIA 用 GitHub/邮箱 + 手机验证（支持 +86）；OpenRouter 用 Google/GitHub/邮箱。Key 分别以 `nvapi-` 和 `sk-or-` 开头。

## 五、适合谁 / 不适合谁

- **NVIDIA 适合**：已在用 NVIDIA 机器/生态的团队、要自托管兜底、要稳定可复现的开源模型推理、对数据落点单一有合规偏好的开发者。
- **NVIDIA 不适合**：要 GPT/Claude 这类前沿闭源模型、要现成多模型自动兜底、不想碰容器的轻量用户。
- **OpenRouter 适合**：一个 Key 试遍模型、做高可用 Fallback、要前沿模型（付费档）、快速原型验证。
- **OpenRouter 不适合**：强合规（HIPAA/严格数据驻留）且不能做显式 ZDR 路由的团队、对延迟极度敏感的实时场景。

## 六、踩坑 3 条

1. **NVIDIA 的「40 RPM」是跨模型共享**，不是每个模型各 40。小模型（如 1B/3B）RPM 更松，批量拆小模型更稳；部分模型（含个别 Nemotron 旗舰）在目录里列着却标「Unavailable」，标准 Key 调不动，别照着目录硬上。
2. **OpenRouter 免费阵容会轮换**，且免费路由「今天选的模型明天可能换」。评估、自动化测试、要稳定输出的任务，**务必钉死具名模型**，别用 `openrouter/free` 跑生产。
3. **失败请求也吃额度**：OpenRouter 免费档每日 50 次，一个写崩的重试循环几分钟烧光；务必加退避和次数上限。NVIDIA 同理，40 RPM 超限会被限流。

## 七、怎么接进你的工作流（路由示例）

把 06 那套 ROUTER 再扩两行——NVIDIA 当「自营开源主力」，OpenRouter 当「聚合兜底」：

```python
ROUTER = {
    "long_context": {"base_url": "https://api.siliconflow.cn/v1",       "model": "deepseek-ai/DeepSeek-V3"},
    "coding":       {"base_url": "https://api.groq.com/openai/v1",      "model": "openai/gpt-oss-120b"},
    "nvidia_first": {"base_url": "https://integrate.api.nvidia.com/v1", "model": "nvidia/llama-3.3-nemotron-super-49b-v1.5"},
    "aggregator":   {"base_url": "https://openrouter.ai/api/v1",        "model": "openrouter/free"},
    "fallback":     {"base_url": "https://openrouter.ai/api/v1",        "model": "z-ai/glm-5.2:free"},
}
```

> 一句话：NVIDIA 是「自家厨房」，OpenRouter 是「外卖平台」。免费档里，要稳、要可控、要能搬回家选 NVIDIA；要全、要兜底、要前沿选 OpenRouter。两者 OpenAI 兼容，改两行就能互换，全接进来最香。

## 八、系列导航 & 下一篇预告

下一篇（08）我们聊**国外「云 + 编码」免费档**：AMD、Ollama 云、opencode——尤其把「opencode 是 AI 编程 Agent、不是 provider」这个边界给读者讲明白。

**系列导航**：01 国内 6 大厂横评 → 02 魔搭/硅基 → 03 国内小众站 → 04 个人 AI 工作流 → 05 国外免费大盘点 → 06 Groq+OpenRouter 实测 → **07 NVIDIA vs OpenRouter 深度对比** → 08 云+编码免费档

> 全系列免费额度数据以官网实时为准，本文核验日期 **2026-09-05**。NVIDIA 免费档额度引自 build.nvidia.com 与 free-model.com（2026-09 核验）；OpenRouter 引自官方博客/FAQ 与 2026 第三方测评。完整可更新版与对照表将同步至 GitHub 仓库（系列收口时开放），欢迎 star 与纠错投稿。
