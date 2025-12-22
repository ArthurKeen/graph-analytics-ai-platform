# CRITICAL BUG FIX #2: Template Generation Layer

**Bug ID**: #CRITICAL-002  
**Date**: December 22, 2025  
**Status**: ✅ DEBUG LOGGING ADDED - Ready for Investigation  
**Priority**: CRITICAL - Production Blocker

---

## 🔴 The REAL Problem (Discovered After Fix #1)

After implementing Fix #1 (removing dangerous default algorithm), testing revealed:

**The executor fix was correct BUT insufficient!**

### Evidence from Premion Test Run:

```
[EXECUTOR DEBUG] Template to Config Conversion:
  Template algorithm: pagerank  ❌ WRONG! (should be "wcc")
  Vertex collections (17): [ALL collections]  ❌ WRONG! (should be 6)
```

**The templates are wrong BEFORE they reach the executor!**

---

## 🔍 Root Cause Analysis

### Data Flow:

```
1. UseCaseExpert generates use cases ❓
   ↓
2. TemplateGenerator.generate_templates() ❌ BUG HERE!
   • Use case type → algorithm mapping
   • Collection selection logic
   • CollectionSelector integration
   ↓
3. Template saved with WRONG data ❌
   • algorithm="pagerank" (should be "wcc")
   • collections=[17] (should be [6])
   ↓
4. Executor receives wrong template ⚠️
   • Can't fix - template is already wrong!
   ↓
5. Wrong algorithm runs with wrong collections ❌
```

---

## 🎯 Suspected Issues

### Issue #1: Use Case Type Mapping

**Location**: `graph_analytics_ai/ai/templates/generator.py` lines 24-51

```python
USE_CASE_TO_ALGORITHM = {
    UseCaseType.COMMUNITY: [
        AlgorithmType.WCC,  # ✅ This is correct
        AlgorithmType.SCC,
        AlgorithmType.LABEL_PROPAGATION
    ],
    # ... other mappings
}
```

**Question**: Is the use case being generated with `use_case_type = UseCaseType.COMMUNITY`?

**Hypothesis**: The LLM might be generating use cases with the WRONG type (e.g., `UseCaseType.CENTRALITY` or `UseCaseType.PATHFINDING` instead of `UseCaseType.COMMUNITY`).

### Issue #2: Collection Selection

**Location**: `graph_analytics_ai/ai/templates/generator.py` lines 185-206

The `CollectionSelector` is being called correctly, BUT:

**Hypothesis #1**: `CollectionSelector` might be failing with an exception, causing fallback to wrong collections.

**Hypothesis #2**: `CollectionSelector` is working, but its output (6 collections) is being overridden somewhere after.

**Hypothesis #3**: The `collection_hints` are not being passed correctly to `CollectionSelector`.

### Issue #3: Fallback Logic

**Location**: `graph_analytics_ai/ai/templates/generator.py` lines 210-220

If `CollectionSelector` fails or returns empty, there's a fallback that grabs ALL collections (up to 5, but still wrong).

---

## ✅ Debug Logging Added

### In `generate_templates()` method:

**What it logs**:
- Number of use cases
- Core/satellite collection hints
- Whether CollectionSelector is available
- **For each use case**:
  - Use case type
  - Use case data needs
  - Algorithm mapping result
  - Selected primary algorithm
  - Final template content

**Sample output expected**:
```
[TEMPLATE DEBUG] Starting template generation for 3 use cases
[TEMPLATE DEBUG] Core collections: ['Device', 'IP', 'AppProduct', 'Site', 'InstalledApp', 'SiteUse']
[TEMPLATE DEBUG] Satellite collections: ['Location', 'Publisher', 'Exchange', ...]
[TEMPLATE DEBUG] CollectionSelector available: True

[TEMPLATE DEBUG] Processing use case: Household Identity Clustering
  ID: UC-S01
  Type: UseCaseType.COMMUNITY  ← Should be this!
  Data needs: ['Device data', 'IP addresses', ...]
[TEMPLATE DEBUG] Mapped use case type 'UseCaseType.COMMUNITY' to algorithms: ['wcc', 'scc', 'label_propagation']
[TEMPLATE DEBUG] Selected primary algorithm: wcc  ← Should be this!
```

### In `_create_template()` method:

**What it logs**:
- Use case details
- Algorithm type selected
- Core/satellite hints
- Collections extracted from use case
- **CollectionSelector execution**:
  - Whether it's available
  - Input parameters
  - Output collections
  - Reasoning
  - Any errors
- Final collections used in template

**Sample output expected**:
```
[TEMPLATE DEBUG] Creating template for: Household Identity Clustering
[TEMPLATE DEBUG] Selected algorithm type: AlgorithmType.WCC
[TEMPLATE DEBUG] Core collections hint: ['Device', 'IP', ...]
[TEMPLATE DEBUG] Satellite collections hint: ['Location', 'Publisher', ...]

[TEMPLATE DEBUG] Extracted from use case data needs:
  Vertex collections (2): ['Device', 'IP']  ← Initial extraction
  
[TEMPLATE DEBUG] CollectionSelector is available, attempting to use it...
[TEMPLATE DEBUG] CollectionSelector returned:
  Vertex collections (6): ['Device', 'IP', 'AppProduct', 'Site', 'InstalledApp', 'SiteUse']
  Reasoning: "For WCC, using core collections only..."
  
[TEMPLATE DEBUG] OVERRIDE: Using CollectionSelector results
[TEMPLATE DEBUG] FINAL collections for template:
  Vertex collections (6): ['Device', 'IP', 'AppProduct', 'Site', 'InstalledApp', 'SiteUse']
```

---

## 📁 Files Modified

### `graph_analytics_ai/ai/templates/generator.py`

**Changes**:
1. `generate_templates()` method (lines 112-173):
   - Added debug logging for workflow initialization
   - Added debug logging for each use case processing
   - Shows algorithm mapping decision
   - Shows final template content

2. `_create_template()` method (lines 175-370):
   - Added debug logging at start (use case details, algorithm selection)
   - Added debug logging for collection extraction
   - Added debug logging for CollectionSelector execution
   - Added debug logging for fallback logic
   - Added debug logging for final collections

**Total changes**: ~80 new print statements for comprehensive tracing

---

## 🧪 What to Look For in Test Run

When Premion runs their workflow, we need to check:

### 1. Use Case Type
```
[TEMPLATE DEBUG] Use case type: UseCaseType.COMMUNITY  ← Should be this!
```

**If it's NOT `UseCaseType.COMMUNITY`**:
- Bug is in UseCaseExpert (LLM prompt or parsing)
- Need to fix use case generation prompt
- Need to ensure "household clustering" maps to COMMUNITY

### 2. Algorithm Mapping
```
[TEMPLATE DEBUG] Mapped use case type 'UseCaseType.COMMUNITY' to algorithms: ['wcc', ...]
[TEMPLATE DEBUG] Selected primary algorithm: wcc  ← Should be this!
```

**If algorithm is NOT `wcc`**:
- Bug is in `USE_CASE_TO_ALGORITHM` mapping
- OR use case type is wrong (see #1)

### 3. CollectionSelector Execution
```
[TEMPLATE DEBUG] CollectionSelector is available, attempting to use it...
[TEMPLATE DEBUG] CollectionSelector returned:
  Vertex collections (6): [...]  ← Should be 6!
```

**If CollectionSelector fails or returns wrong count**:
- Bug is in CollectionSelector logic
- OR collection_hints not passed correctly
- Check for exception messages

### 4. Final Template
```
[TEMPLATE DEBUG] FINAL collections for template:
  Vertex collections (6): ['Device', 'IP', 'AppProduct', 'Site', 'InstalledApp', 'SiteUse']
```

**If final count is NOT 6**:
- Collections being overridden after CollectionSelector
- Fallback logic activating incorrectly
- Need to trace where the override happens

---

## 🚀 Next Steps

### For Premion Team:

1. **Pull latest fix**:
   ```bash
   cd ~/code/graph-analytics-ai-platform
   git pull origin feature/ai-foundation-phase1
   ```

2. **Run workflow**:
   ```bash
   cd ~/code/premion-graph-analytics
   python scripts/run_household_analysis.py 2>&1 | tee debug_output.txt
   ```

3. **Look for these patterns** in `debug_output.txt`:
   ```bash
   grep "\[TEMPLATE DEBUG\]" debug_output.txt
   grep "Use case type:" debug_output.txt
   grep "Selected primary algorithm:" debug_output.txt
   grep "CollectionSelector returned:" debug_output.txt
   grep "FINAL collections:" debug_output.txt
   ```

4. **Share findings**:
   - What is the use case type?
   - What algorithm was selected?
   - Did CollectionSelector run? What did it return?
   - What are the final collections?

### For Library Team (After Getting Logs):

Based on the debug output, we'll know:
- **If bug is in use case generation**: Fix LLM prompt or parsing
- **If bug is in algorithm mapping**: Fix USE_CASE_TO_ALGORITHM or add logic
- **If bug is in CollectionSelector**: Fix selection logic or integration
- **If bug is in fallback**: Fix fallback conditions or logic

---

## 📊 Expected vs Actual

### Expected Debug Output:
```
[TEMPLATE DEBUG] Use case type: UseCaseType.COMMUNITY
[TEMPLATE DEBUG] Selected primary algorithm: wcc
[TEMPLATE DEBUG] CollectionSelector returned:
  Vertex collections (6): ['Device', 'IP', 'AppProduct', 'Site', 'InstalledApp', 'SiteUse']
[TEMPLATE DEBUG] FINAL collections:
  Vertex collections (6): ['Device', 'IP', 'AppProduct', 'Site', 'InstalledApp', 'SiteUse']
```

### Actual Debug Output (from last run):
```
??? Use case type: ???
??? Selected primary algorithm: pagerank  ❌
??? CollectionSelector returned: ???
??? FINAL collections:
  Vertex collections (17): [ALL collections]  ❌
```

---

## 📝 Commit Message

```
debug: Add comprehensive logging to template generation layer

CRITICAL BUG FIX #2 - Template layer investigation

Problem:
- After Fix #1 (executor), testing showed templates are ALREADY wrong
- Templates have algorithm="pagerank" (should be "wcc")
- Templates have 17 collections (should have 6)
- Bug is in template generation, not execution

Investigation Strategy:
Add comprehensive debug logging to trace:
1. Use case type assignment
2. Algorithm mapping from use case type
3. Collection extraction from use case
4. CollectionSelector execution and results
5. Final template content

Logging Added:
- generate_templates(): Shows use case processing and algorithm selection
- _create_template(): Shows collection selection flow and CollectionSelector integration
- ~80 print statements for complete tracing

Expected Insights:
- Is use case type correct? (should be COMMUNITY)
- Is algorithm mapping working? (COMMUNITY → WCC)
- Is CollectionSelector being called and working?
- Where do collections expand from 6 to 17?

Next Steps:
- Premion team runs workflow with new logging
- Analyze debug output to find exact failure point
- Fix identified issue (use case gen, mapping, or selector)
- Re-test

Related: Fix #1 (executor dangerous default) was valid but insufficient
Status: Ready for investigation
```

---

## ✅ Status

- **Investigation #1 (Executor)**: ✅ COMPLETE - Fixed dangerous default
- **Investigation #2 (Templates)**: 🔄 IN PROGRESS - Debug logging added
- **Testing**: ⏸️ WAITING FOR CUSTOMER
- **Final Fix**: ⏸️ PENDING DEBUG OUTPUT

---

**Debug logging is comprehensive. Now we'll see EXACTLY where the bug is!** 🔍

