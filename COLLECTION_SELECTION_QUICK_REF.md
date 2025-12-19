# Collection Selection - Quick Reference for Customer Projects

## 📋 TL;DR

Tell the library which collections are "satellites" (reference data) vs "core" (main entities):

```python
from graph_analytics_ai.ai.templates import TemplateGenerator

generator = TemplateGenerator(
    graph_name="your_graph",
    satellite_collections=["metadata", "configs", "lookups"],  # Exclude from WCC/SCC
    core_collections=["users", "products", "orders"]           # Main entities
)

templates = generator.generate_templates(use_cases, schema)
```

**Result**:
- ✅ WCC/SCC exclude satellites → meaningful components
- ✅ PageRank/Betweenness include everything → accurate scores
- ✅ Automatic and transparent

---

## 🎯 For Your Premion Project

### Step 1: Identify Collections

**Satellite Collections** (exclude from WCC/SCC):
```python
satellite_collections = [
    "audience_metadata",      # Descriptive info
    "device_specs",           # Technical specs
    "geo_lookups",            # Reference data
    "rate_cards",             # Pricing info
    # Add any other reference/lookup tables
]
```

**Core Collections** (main graph):
```python
core_collections = [
    "audiences",              # Primary entities
    "campaigns",
    "creatives",
    "devices",
    "publishers",
    "placements",
    # Add other main business entities
]
```

### Step 2: Configure Generator

```python
from graph_analytics_ai.ai.templates import TemplateGenerator

generator = TemplateGenerator(
    graph_name="premion_media_graph",
    satellite_collections=satellite_collections,
    core_collections=core_collections
)
```

### Step 3: Generate and Review

```python
templates = generator.generate_templates(use_cases, schema)

# Review what was selected
for template in templates:
    algo = template.algorithm.algorithm.value
    colls = template.config.vertex_collections
    reasoning = template.metadata['collection_selection_reasoning']
    
    print(f"{algo}: {colls}")
    print(f"  Why: {reasoning}\n")
```

---

## 🔍 Test Before Executing

```python
from graph_analytics_ai.ai.templates import select_collections_for_algorithm, AlgorithmType

# Preview WCC selection
wcc = select_collections_for_algorithm(
    AlgorithmType.WCC,
    schema,
    satellite_collections=["audience_metadata"]
)
print(f"WCC uses: {wcc.vertex_collections}")
print(f"WCC excludes: {wcc.excluded_vertices}")

# Preview PageRank selection
pr = select_collections_for_algorithm(
    AlgorithmType.PAGERANK,
    schema,
    satellite_collections=["audience_metadata"]
)
print(f"PageRank uses: {pr.vertex_collections}")  # Should be ALL
```

---

## 🎨 What Gets Selected?

| Algorithm | Satellites? | Collections Used | Why |
|-----------|-------------|------------------|-----|
| **WCC** | ❌ Excluded | Core only | Find meaningful components |
| **SCC** | ❌ Excluded | Core only | Strongly connected core |
| **PageRank** | ✅ Included | Everything | Full graph importance |
| **Betweenness** | ✅ Included | Everything | Accurate centrality |
| **Label Propagation** | ❌ Excluded | Core only | Community detection |

---

## 🚨 Common Issues

### "WCC finding too many components"
**Fix**: Add more collections to `satellite_collections`

### "PageRank scores look wrong"
**Check**: Verify PageRank is using all collections (not excluding important ones)

### "Auto-classification is wrong"
**Fix**: Use explicit `satellite_collections` and `core_collections`

---

## 📚 Full Documentation

- **Complete Guide**: `docs/CUSTOMER_PROJECT_INSTRUCTIONS.md`
- **Deep Dive**: `docs/COLLECTION_SELECTION_GUIDE.md`
- **Implementation**: `docs/COLLECTION_SELECTION_IMPLEMENTATION.md`

---

## ✅ Checklist for Your Project

- [ ] Identify satellite collections (metadata, lookups, configs)
- [ ] Identify core collections (main business entities)
- [ ] Update `TemplateGenerator` initialization with collection roles
- [ ] Test WCC selection (should exclude satellites)
- [ ] Test PageRank selection (should include everything)
- [ ] Review selection reasoning in template metadata
- [ ] Run WCC and verify fewer, more meaningful components
- [ ] Compare results with previous runs (if any)
- [ ] Document collection roles in project README

---

## 🔧 Code Template

Copy this into your Premion project:

```python
from graph_analytics_ai.ai.templates import TemplateGenerator

# Define your collection roles
SATELLITE_COLLECTIONS = [
    "audience_metadata",
    "device_specs",
    "geo_lookups",
    "rate_cards",
    # TODO: Add your satellite collections
]

CORE_COLLECTIONS = [
    "audiences",
    "campaigns",
    "creatives",
    "devices",
    "publishers",
    # TODO: Add your core collections
]

# Initialize generator
generator = TemplateGenerator(
    graph_name="premion_media_graph",
    satellite_collections=SATELLITE_COLLECTIONS,
    core_collections=CORE_COLLECTIONS
)

# Generate templates
templates = generator.generate_templates(use_cases, schema)

# Validate selections
print("\n=== Collection Selections ===")
for template in templates:
    algo = template.algorithm.algorithm.value
    colls = template.config.vertex_collections
    reasoning = template.metadata.get('collection_selection_reasoning', 'N/A')
    excluded = template.metadata.get('excluded_collections', {}).get('vertices', [])
    
    print(f"\n{template.name}")
    print(f"  Algorithm: {algo}")
    print(f"  Uses: {colls}")
    if excluded:
        print(f"  Excludes: {excluded}")
    print(f"  Why: {reasoning}")

# Proceed with execution...
```

---

## 💡 Pro Tips

1. **Start explicit**: Always specify satellite collections in production
2. **Test first**: Use `select_collections_for_algorithm()` to preview
3. **Review reasoning**: Check `template.metadata['collection_selection_reasoning']`
4. **Compare results**: Run WCC with/without satellite exclusion
5. **Document choices**: List your collection roles in project docs

