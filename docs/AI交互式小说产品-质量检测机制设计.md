# AI交互式小说产品 - 质量检测机制设计文档

## 设计理念

### 核心原则
- **分层检测**：必须通过的基础检测 + 可选的质量优化
- **奥卡姆剃刀**：避免过度复杂化，专注用户能感知的质量问题
- **用户体验优先**：平衡质量标准与响应速度
- **成本控制**：合理控制API调用成本，避免过度优化

### 设计哲学
质量检测不是为了追求完美，而是为了确保用户获得"足够好"的体验。MVP阶段重点解决明显的质量问题，避免让用户失望。

## 两层质量检测架构

### 第一层：快速检测（必须通过）
**设计目标**：确保基本可用性，避免明显问题
**处理策略**：检测失败必须重新生成，不允许放行

#### 1. 内容安全检测
**检测目标**：
- 暴力血腥内容过滤
- 成人内容检测
- 政治敏感内容识别
- 仇恨言论过滤

**技术方案**：
- 使用现成的内容审核API（Google Cloud Natural Language、Azure Content Moderator等）
- 多重安全策略：关键词过滤 + AI模型检测
- 检测时间：< 3秒

**失败处理**：
- 直接拒绝内容，要求AI重新生成
- 不向用户暴露具体原因
- 统一显示"正在重新创作中..."

#### 2. 基础逻辑检测
**检测目标**：
- 角色性格前后一致性
- 世界观设定不矛盾（修仙境界、武功体系、科技设定等）
- 情节发展的基本合理性
- 因果关系的逻辑连贯性

**技术方案**：
- 关键信息提取：从当前章节提取角色、设定、情节要素
- 历史对比验证：与故事总结中的历史信息进行一致性检查
- 规则验证：检查是否违反已建立的世界观规则

**检测维度**：
```
角色一致性：
- 性格特征不能突然改变
- 能力水平不能无故跳跃
- 人际关系不能无故逆转

世界观一致性：
- 修仙：境界体系、功法设定、门派关系
- 武侠：武功体系、江湖规则、时代背景
- 科技：技术水平、社会结构、科学设定

情节合理性：
- 事件发展符合因果逻辑
- 角色行为符合动机
- 时间线不能混乱
```

**失败处理**：
- 提供具体错误信息给AI模型
- 要求针对性修正后重新生成
- 最多允许2次修正机会

#### 3. 格式完整性检测
**检测目标**：
- 章节长度符合标准
- 选择生成完整性
- 内容结构完整性

**具体标准**：
```
章节长度：
- 目标：2500字
- 允许范围：2000-3000字（±20%偏差）
- 最低要求：不少于1800字

选择生成：
- 必须生成3个不同选择
- 每个选择长度：15-50字
- 选择内容不能重复或过于相似

内容完整性：
- 章节有明确的开头和结尾
- 没有明显的内容截断
- 不包含"未完成"、"待续"等标记
```

**失败处理**：
- 格式问题直接重新生成
- 不需要复杂的修正逻辑

### 第二层：质量优化（可选重试）
**设计目标**：提升用户体验，确保内容吸引力
**处理策略**：质量不达标时重试，但有次数限制

#### 1. 文笔质量评估
**评估维度**：
```
语言流畅度 (1-10分)：
- 句式是否自然
- 用词是否恰当
- 语法是否正确

情感表达力 (1-10分)：
- 是否能有效传达情感
- 氛围营造是否到位
- 情感层次是否丰富

画面感强度 (1-10分)：
- 描述是否生动具体
- 是否能让读者产生画面感
- 细节描写是否恰当

AI痕迹明显度 (1-10分，越低越好)：
- 是否有明显的AI生成特征
- 语言是否过于机械化
- 是否缺乏人性化表达
```

**技术方案**：
- 使用不同的AI模型进行交叉评估（如用Claude评估Gemini生成的内容）
- 基于结构化prompt的评分机制
- 评估时间：< 10秒

**质量标准**：
- 最低及格线：6.0分
- 目标质量线：7.5分
- 各维度不能有明显短板（单项不低于5.0分）

**失败处理**：
- 提供具体改进建议
- 最多重试2次
- 超过重试次数接受当前质量

#### 2. 情节吸引力评分
**评估维度**：
```
悬念设置 (1-10分)：
- 是否有效制造悬念
- 是否激发读者继续阅读的欲望
- 节奏把控是否恰当

情节推进 (1-10分)：
- 是否有效推动故事发展
- 是否有新的信息或转折
- 与整体故事脉络的契合度

选择设计质量 (1-10分)：
- 选择是否有趣且有意义
- 是否体现不同的价值观
- 选择后果的可预期性

与前文呼应 (1-10分)：
- 是否与之前情节有良好连接
- 是否激活了早期埋下的伏笔
- 角色发展的连续性
```

**质量标准**：
- 最低及格线：6.5分
- 目标质量线：8.0分
- 重点关注选择设计质量（不低于7.0分）

#### 3. 选择差异度检测
**检测目标**：
- 确保3个选择代表不同方向
- 避免选择过于相似
- 体现不同的价值观和风险收益组合

**技术方案**：
- 语义相似度分析
- 选择类型分类（行动型、思考型、情感型等）
- 风险收益评估

**差异度标准**：
```
语义相似度：
- 任意两个选择的相似度 < 70%
- 平均相似度 < 50%

选择类型：
- 至少包含2种不同类型的选择
- 风险等级分布合理

价值观体现：
- 体现不同的道德选择
- 代表不同的行为倾向
- 反映不同的长短期考量
```

**失败处理**：
- 保持章节内容不变
- 只重新生成选择部分
- 最多重试1次

## 用户体验设计

### 等待时间管理
**时间目标**：
- 第一层检测：< 10秒
- 第二层检测：< 20秒
- 总体目标：< 30秒

**用户反馈机制**：
```
检测阶段显示：
- "AI正在精心创作中..." (0-10秒)
- "正在优化故事质量..." (10-20秒)
- "即将完成，请稍候..." (20-30秒)

进度指示：
- 简单的进度条或动画
- 避免显示具体的技术细节
- 营造"AI在认真创作"的感觉
```

### 失败处理策略
**用户体验原则**：
- 不向用户暴露技术细节
- 统一的重试提示信息
- 避免让用户感到系统"出错"

**处理流程**：
```
检测失败 → 自动重试 → 用户无感知
重试失败 → 降级策略 → 接受较低质量
系统异常 → 友好提示 → 建议稍后重试
```

### 质量标准的平衡
**MVP阶段策略**：
- **严格执行第一层**：确保不出现明显问题，维护产品声誉
- **适度执行第二层**：平衡质量和速度，避免过度优化
- **设置合理期待**：让用户理解AI创作需要时间

**成本控制**：
- 第一层检测：必要成本，不可省略
- 第二层检测：可优化成本，根据用户反馈调整严格程度
- 重试策略：限制重试次数，避免成本失控

## 降级策略

### 检测超时处理
**超时阈值**：30秒
**处理方式**：
- 接受当前最佳结果
- 记录超时事件，用于后续优化
- 向用户道歉并说明情况

### 质量不达标处理
**处理原则**：
- 第一层不达标：必须重试或拒绝
- 第二层不达标：可以接受，但记录质量数据
- 连续质量问题：触发人工审核机制

### 系统异常处理
**异常类型**：
- API服务不可用
- 网络连接问题
- 模型响应异常

**处理策略**：
- 自动重试机制（最多3次）
- 降级到更简单的检测方式
- 提供友好的错误提示

## 质量数据收集

### 数据指标
**检测效果指标**：
- 第一层检测通过率
- 第二层检测平均分数
- 重试次数分布
- 用户满意度反馈

**性能指标**：
- 检测平均耗时
- API调用成本
- 系统稳定性

### 持续优化
**优化方向**：
- 根据用户反馈调整质量标准
- 优化检测算法提升效率
- 平衡质量要求与成本控制

## 实施计划

### MVP阶段重点
1. **优先实现第一层检测**：确保基本可用性
2. **简化第二层检测**：重点关注明显的质量问题
3. **建立数据收集机制**：为后续优化提供依据

### 后续迭代方向
1. **智能化检测**：基于用户行为数据优化检测标准
2. **个性化质量**：根据用户偏好调整质量要求
3. **成本优化**：提升检测效率，降低运营成本

---

*文档创建时间：2025年*
*讨论参与者：产品构思者 & Sean(deepractice.ai)*
*设计原则：奥卡姆剃刀 + 用户体验优先 + 矛盾驱动决策*
