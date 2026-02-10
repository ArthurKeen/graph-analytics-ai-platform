# Business Requirements Document Template

**Purpose:** This template helps you define your domain for AI-powered graph analytics. The information you provide will be used to generate a custom industry vertical that understands your specific business context.

---

## 1. Domain Overview (REQUIRED)

**Industry/Vertical:** [e.g., Supply Chain, Healthcare, Cybersecurity, E-Commerce]

**Primary Business Function:** [e.g., Optimize logistics, Detect fraud, Track disease spread, Recommend products]

**Target Users/Stakeholders:** [e.g., Supply chain analysts, Risk managers, Epidemiologists, Data scientists]

**Business Problem:** [What problem are you solving with graph analytics?]

---

## 2. Domain Terminology (REQUIRED)

### Currency & Financial Units
**Primary Currency:** [e.g., USD, EUR, GBP, ₹ Crores, ¥]

**Measurement Units:** [e.g., units, pallets, containers, days, patients, transactions, devices]

### Key Domain Terms
Define the most important terms in your domain:

| Term | Definition |
|------|------------|
| [Term 1] | [Brief definition] |
| [Term 2] | [Brief definition] |
| [Term 3] | [Brief definition] |

### Regulatory & Compliance Context
**Relevant Regulations:** [e.g., GDPR, HIPAA, SOX, PMLA, FDA regulations]
- [Regulation 1]: [Brief description and relevance]
- [Regulation 2]: [Brief description and relevance]

### Important Thresholds & Benchmarks
Define critical values in your domain:

| Threshold Name | Value | Meaning |
|----------------|-------|---------|
| [e.g., Critical inventory] | [< 7 days] | [Stock level requiring immediate action] |
| [e.g., High risk concentration] | [> 30% of volume] | [Dangerous dependency on single entity] |

---

## 3. Graph Structure (REQUIRED)

### Node Types
For each major entity type in your graph, describe:

| Node Type | Business Meaning | Key Attributes | Typical Volume |
|-----------|------------------|----------------|----------------|
| [e.g., Supplier] | [Manufacturers and vendors] | [name, location, capacity] | [500-1000] |
| [e.g., Warehouse] | [Distribution centers] | [location, capacity, inventory] | [20-50] |
| [e.g., Product] | [SKUs and items] | [sku, category, price] | [10,000+] |

### Edge Types
For each relationship type in your graph, describe:

| Edge Type | Business Meaning | Direction | What It Represents |
|-----------|------------------|-----------|-------------------|
| [e.g., suppliesTo] | [Supply relationships] | [Directed] | [Supplier → Warehouse shipments] |
| [e.g., stores] | [Inventory storage] | [Directed] | [Warehouse → Product inventory] |
| [e.g., dependsOn] | [Supply dependencies] | [Directed] | [Product → Supplier requirements] |

---

## 4. Key Metrics & KPIs (REQUIRED)

What metrics define success or risk in your domain?

| Metric Name | Definition | Normal Range | Critical Threshold |
|-------------|------------|--------------|-------------------|
| [e.g., Lead time variance] | [Std dev of delivery times] | [2-5 days] | [> 10 days] |
| [e.g., Inventory turnover] | [Sales / Avg inventory] | [4-6x per year] | [< 2x per year] |
| [e.g., Concentration risk] | [% from single source] | [< 20%] | [> 30%] |

---

## 5. Patterns to Detect (REQUIRED)

### Critical Patterns (What's BAD/RISKY?)
Define 2-5 patterns that indicate problems:

**Pattern 1: [Name]**
- **Description:** [What this pattern indicates]
- **Indicators:** 
  - [Signal 1]
  - [Signal 2]
  - [Signal 3]
- **Business Impact:** [What happens if detected? What's at risk?]
- **Example:** [Concrete example from your domain]

**Pattern 2: [Name]**
- **Description:** ...
- **Indicators:** ...
- **Business Impact:** ...
- **Example:** ...

### Valuable Patterns (What's GOOD/OPPORTUNITY?)
Define 1-3 patterns that indicate opportunities:

**Pattern 1: [Name]**
- **Description:** [What this pattern indicates]
- **Value:** [What opportunity does this present?]
- **Example:** [Concrete example]

### Anomalies (What's UNUSUAL?)
What patterns are neither good nor bad, but warrant investigation?

---

## 6. Risk Classification (OPTIONAL but recommended)

Define how findings should be classified:

| Risk Level | Definition | Response Time | Example |
|------------|------------|---------------|---------|
| **CRITICAL** | [Immediate threat, severe impact] | [0-4 hours] | [Single point of failure detected] |
| **HIGH** | [Significant risk, needs attention] | [24-48 hours] | [Above-threshold concentration] |
| **MEDIUM** | [Moderate concern, monitor] | [1 week] | [Suboptimal but not dangerous] |
| **LOW** | [Minor issue, informational] | [As convenient] | [Optimization opportunity] |

---

## 7. Action Framework (OPTIONAL but recommended)

What should analysts DO when patterns are detected?

### Immediate Actions (0-24 hours)
| Pattern Type | Action | Who to Notify | Process |
|--------------|--------|---------------|---------|
| [e.g., Single point of failure] | [Identify backups, escalate] | [Procurement manager] | [Emergency sourcing protocol] |

### Short-term Actions (1-7 days)
| Pattern Type | Action | Process |
|--------------|--------|---------|
| [e.g., High concentration] | [Diversification plan] | [Multi-sourcing strategy] |

### Long-term Actions (Strategic)
| Pattern Type | Action | Timeline |
|--------------|--------|----------|
| [e.g., Geographic risk] | [Regional expansion] | [6-12 months] |

---

## 8. Example Insights (HIGHLY RECOMMENDED)

Provide 2-3 examples of what **good insights** look like in your domain:

### Good Insight Example #1

```
Title: Single Point of Failure: Supplier S-123 Provides 40% of Critical Components

Description: Supplier S-123 (located in Region A) is the sole provider of Component X, 
which is used in 40% of our product line (Products P-001 through P-145). No backup 
suppliers exist in any region. Lead time is 45 days. Current inventory: 12 days. 
Historical reliability: 85% (15% late deliveries in past 12 months).

Geographic Analysis: 3 other suppliers in Region A provide non-critical components, 
creating additional regional concentration. Region A has faced 2 major disruptions 
in past 5 years (flood 2021, port strike 2023).

Business Impact: 
- RISK: Supply disruption would halt 40% of production within 12 days
- FINANCIAL: Estimated revenue impact: $2.4M/week if disrupted
- OPERATIONS: No viable short-term alternatives identified
- STRATEGIC: This component is critical to Q2 product launch

Recommended Actions:
IMMEDIATE (0-24 hrs):
  - Flag S-123 for enhanced monitoring
  - Review current inventory levels daily
  - Add to weekly exec risk dashboard
  
SHORT-TERM (1-4 weeks):
  - Identify and qualify backup suppliers (target: 2 sources within 60 days)
  - Negotiate safety stock terms with S-123
  - Explore design alternatives that reduce dependency
  
LONG-TERM (3-6 months):
  - Implement multi-sourcing for all critical components
  - Diversify to suppliers in Region B or C
  - Develop component substitution matrix

Confidence: 0.92
Risk Level: CRITICAL
```

**Why this is good:**
- ✓ Specific entity IDs (S-123, Products P-001-P-145)
- ✓ Quantified impact ($2.4M/week, 40% of product line)
- ✓ Business context (Q2 launch, historical reliability)
- ✓ Risk classification (CRITICAL)
- ✓ Actionable recommendations with timelines
- ✓ High confidence score

### Good Insight Example #2

[Another example specific to your domain]

---

### Bad Insight Example (What to AVOID)

```
Title: Potential Issue Found

Description: Some suppliers show unusual patterns that may indicate risk.

Business Impact: Should investigate further.

Confidence: 0.35
```

**Why this is bad:**
- ✗ No specific entities identified
- ✗ "Unusual patterns" is vague
- ✗ No quantification of risk or impact
- ✗ No actionable recommendations
- ✗ No business context
- ✗ Low confidence indicates uncertainty

---

## 9. Graph Analytics Goals (REQUIRED)

What specific analyses do you want to perform?

### Primary Goals
1. **[Goal 1]:** [e.g., Identify single points of failure in supply network]
   - **Algorithm:** [e.g., WCC - find critical components with no alternatives]
   - **Success Criteria:** [e.g., Flag all components with <2 suppliers]

2. **[Goal 2]:** [e.g., Detect concentration risk]
   - **Algorithm:** [e.g., PageRank - identify over-leveraged suppliers]
   - **Success Criteria:** [e.g., Alert when >30% volume from single source]

3. **[Goal 3]:** [e.g., Optimize distribution routing]
   - **Algorithm:** [e.g., Shortest path, betweenness centrality]
   - **Success Criteria:** [e.g., Reduce average lead time by 15%]

### Secondary Goals
- [Goal 4]
- [Goal 5]

---

## 10. Success Criteria (REQUIRED)

How will you know if the graph analytics are providing value?

### Quantitative Metrics
- [Metric 1]: [e.g., Detect 90%+ of known issues]
- [Metric 2]: [e.g., < 10% false positive rate]
- [Metric 3]: [e.g., Reduce investigation time by 50%]

### Qualitative Outcomes
- [Outcome 1]: [e.g., Analysts can identify risks in minutes vs hours]
- [Outcome 2]: [e.g., Recommendations are actionable and specific]
- [Outcome 3]: [e.g., Reports are understandable to non-technical stakeholders]

---

## 11. Data Quality Notes (OPTIONAL)

**Data Completeness:**
- [e.g., 95% of suppliers have location data]
- [e.g., 40% of products missing category classification]

**Known Data Issues:**
- [e.g., Historical transactions before 2022 may be incomplete]
- [e.g., Some edge relationships are inferred, not definitive]

**Update Frequency:**
- [e.g., Graph updated daily at 2am]
- [e.g., Some data sources lag by 24-48 hours]

---

## 12. Stakeholder Information (OPTIONAL)

**Primary Stakeholders:**
- [Name/Role]: [e.g., Sarah Chen, VP Supply Chain] - [Primary user]
- [Name/Role]: [e.g., Risk Management Team] - [Weekly reports]

**Executive Sponsor:**
- [Name/Role]: [e.g., James Liu, COO]

**Technical Contacts:**
- [Name/Role]: [e.g., Data Engineering team] - [For data issues]

---

## Notes for AI Vertical Generation

This document will be analyzed by an AI agent to generate a custom industry vertical. The more specific and detailed you are, especially in sections 1-5 and 8 (example insights), the better the generated analysis will be.

**Key sections for high-quality generation:**
1. ✅ Domain terminology (section 2) - Be comprehensive
2. ✅ Graph structure (section 3) - List all major node/edge types
3. ✅ Patterns to detect (section 5) - Provide specific indicators
4. ✅ Example insights (section 8) - **This is the most important section!**

The example insights (section 8) teach the AI what "good" looks like in your domain. Provide real or realistic examples with specific numbers, entity IDs, and actionable recommendations.

---

**Document Version:** 2.0 (Enhanced for Custom Vertical Generation)  
**Last Updated:** [Date]  
**Author:** [Your Name/Team]
