# 商品销售战略报告模板

## 写作原则

这是品牌方和商品负责人用来决策的报告。让读者从标题就能看懂思路；保留「产品差异（Product Differentiation）」「痛点挖掘（Pain Point Mining）」等中英双语结构词，但不出现任何参考仓库、框架作者、agent 或方法来源。

报告要有说服力，不要把研究过程、证据等级和免责声明放在前台。只有在评论对象、价格成本和关键主张可能被误解时，简短说明边界。

## 推荐结构

```markdown
# [商品／SKU] 新品销售战略报告（New Product Sales Strategy）

> 分析对象：
> 目标市场：
> 销售渠道：
> 本轮目标：

## 结论摘要（Executive Summary）
[5—8 条直接决策：主推什么、谁会买、核心钩子、价格、商品角色、最重要验证]

# 阶段一：产品差异与市场机会（Product Differentiation & Market Opportunity）

## 1. 产品机会判断（Product Opportunity Assessment）
### 产品事实基线
### 竞争者对照矩阵（Competitor Comparison Matrix）
[表后必须有判断]

## 2. 痛点挖掘（Pain Point Mining）
### 评论／搜索主题与频次
### 核心痛点（Core Pain Points）
### 消费者语言（Voice of Customer）

## 3. 市场空位（Market White Space）
[空位表＋从日常问题到品牌资格的销售链]

# 阶段二：目标购买人群（Target Customer）

## 4. 候选人群评估（Audience Segment Evaluation）
## 5. 核心买家画像（Primary Buyer Persona）
[人口与支付能力假设、行为、心理、购买场景、推测依据]
## 6. 痛点与欲望矩阵（Pain–Desire Matrix）
## 7. 购买认知路径（Buyer Awareness Journey）

# 阶段三：销售主张提炼（Sales Proposition Development）

## 8. 故事资产盘点（Story Asset Inventory）
## 9. 传播钩子开发（Hook Development）
## 10. 推荐方向（Recommended Direction）
[钩子、单一核心主张、品牌大故事及三者分工]
## 11. 证明库（Proof Arsenal）
## 12. 异议处理（Objection Handling）

# 阶段四：商品与价格策略（Product & Pricing Strategy）

## 13. SKU 角色设计（SKU Role Design）
## 14. 价格参照（Price Benchmark）
## 15. 推荐价格架构（Price Architecture）
## 16. 价格价值表达（Price–Value Framing）
## 17. 单位经济闸门（Unit Economics Guardrail）

# 阶段五：上市打法与验证（Go-to-Market & Validation）

## 18. 内容角度测试（Message Angle Testing）
## 19. 首方数据采集（First-Party Data Collection）
## 20. 保留／调整／撤回条件

# 最终决策卡（Final Decision Card）
[一页内汇总主推商品、人群、痛点、钩子、核心主张、故事、价格和下一阶段]

# 主要资料来源（Sources）
[按商品／品牌、品类／权威、评论／竞品、价格／渠道分组]
```

## 输出质量

- 开头 10% 已经回答最重要的商业决定；
- 「痛点」不是主题名，而是顾客的两难或失败体验；
- 目标顾客具体到谁会为建议价买单；
- 核心主张只有一个，辅助故事有明确分工；
- 价格是明确人民币数字，不只给区间；
- 每个关键结论都有事实、市场线索或推理链；
- 报告中不出现内部候选评分和 method attribution；
- 最终决策卡可直接喂给下游文案 agent。
- 报告定稿后同步更新 `internal/messaging-matrix.md`，并从同一 Markdown 导出分享版 PDF；不得为 PDF 另写一份摘要报告。
