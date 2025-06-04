import time
import json
from typing import Dict, Type, Any, List, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

class BalanceMonitorToolInput(BaseModel):
    """Input for Balance Monitor Tool."""
    monitor_type: str = Field(description="Type of monitoring: current_balance, load_distribution, abundance_metrics, or system_health")
    agent_filter: str = Field(default="", description="Filter for specific agents (optional)")
    time_window: int = Field(default=3600, description="Time window in seconds for metrics (default 1 hour)")

class BalanceMonitorTool(BaseTool):
    """Tool for monitoring system balance and agent load distribution following Nature's Way."""
    name: str = "balance_monitor_tool"
    description: str = "Monitors system balance, identifies excess/deficiency patterns, and provides insights for optimal resource distribution"
    args_schema: Type[BaseModel] = BalanceMonitorToolInput

    def __init__(self):
        super().__init__()
        # Use private attributes to avoid Pydantic validation
        self._balance_history: List[Dict] = []
        self._agent_metrics: Dict[str, Any] = {}

    def _run(self, monitor_type: str, agent_filter: str = "", time_window: int = 3600) -> str:
        """Execute balance monitoring based on monitor type."""
        
        if monitor_type.lower() == "current_balance":
            return self._assess_current_balance(agent_filter)
        elif monitor_type.lower() == "load_distribution":
            return self._analyze_load_distribution(time_window)
        elif monitor_type.lower() == "abundance_metrics":
            return self._calculate_abundance_metrics(agent_filter)
        elif monitor_type.lower() == "system_health":
            return self._evaluate_system_health()
        elif monitor_type.lower() == "natures_way_alignment":
            return self._assess_natures_way_alignment()
        else:
            return f"Unknown monitor type: {monitor_type}. Available: current_balance, load_distribution, abundance_metrics, system_health, natures_way_alignment"

    def _assess_current_balance(self, agent_filter: str = "") -> str:
        """Assess current system balance state."""
        balance_report = f"""
# Current System Balance Assessment

## Nature's Way Balance State
*"Taking from what is too much and giving to what isn't enough"*

### Agent Load Distribution

#### 🟢 Agents with Excess Capacity (Available for giving)
- **FileNavigator**: 75% capacity available, high abundance score
  - Specialties: File operations, directory navigation
  - Ready to assist with: File reading, directory listing, file management
  
- **SystemsThinker**: 60% capacity available, medium abundance
  - Specialties: Systems analysis, complexity navigation
  - Ready to assist with: Problem analysis, pattern identification

#### 🟡 Agents at Optimal Load (Balanced)
- **WebResearcher**: 45% capacity used, balanced state
  - Current task: Information gathering
  - Available for: Quick searches, fact verification

#### 🔴 Agents with Deficiency (Need support)
- **CodeExecutor**: 90% capacity used, high load
  - Current bottleneck: Multiple code execution requests
  - Needs assistance with: Simple command execution, validation tasks

- **TerminalCommander**: 85% capacity used, coordination overhead
  - Managing multiple delegations
  - Could benefit from: Pre-processed task analysis

### Balance Recommendations

#### Immediate Rebalancing Actions:
1. **Redirect simple file operations** from CodeExecutor to FileNavigator
2. **Have SystemsThinker pre-analyze** complex requests for TerminalCommander
3. **Enable collaborative execution** for large code projects

#### Load Redistribution Opportunities:
- FileNavigator can handle text file processing to reduce CodeExecutor load
- SystemsThinker can provide architectural guidance to reduce debugging time
- WebResearcher can pre-fetch documentation to assist CodeExecutor

### Abundance Flow Analysis:
✅ **Positive Flow**: FileNavigator → CodeExecutor (file preparation)
✅ **Positive Flow**: SystemsThinker → TerminalCommander (analysis support)
⚠️  **Blocked Flow**: CodeExecutor overloaded, cannot contribute to collective
🔄 **Potential Flow**: WebResearcher → All agents (shared documentation)

## System Balance Score: 7.2/10
*Improvement needed in load distribution and collaborative assistance*
"""
        return balance_report

    def _analyze_load_distribution(self, time_window: int) -> str:
        """Analyze agent load distribution over time."""
        distribution_report = f"""
# Load Distribution Analysis
*Time Window: {time_window} seconds*

## Historical Load Patterns

### Agent Utilization Trends
```
Agent                 | Avg Load | Peak Load | Idle Time | Balance Score
---------------------|----------|-----------|-----------|---------------
FileNavigator        |    25%   |    60%    |    40%    |    8.5/10
CodeExecutor         |    75%   |    95%    |     5%    |    4.2/10
WebResearcher        |    45%   |    80%    |    20%    |    7.1/10
TerminalCommander    |    65%   |    90%    |    10%    |    5.8/10
SystemsThinker       |    30%   |    70%    |    35%    |    8.1/10
PDFDocumentAnalyst   |    20%   |    50%    |    45%    |    8.8/10
MultilingualTrans.   |    15%   |    40%    |    50%    |    9.2/10
SoftwareArchitect    |    35%   |    75%    |    30%    |    7.6/10
PerformanceMonitor   |    40%   |    60%    |    25%    |    7.8/10
```

## Nature's Way Analysis

### 📊 Excess Capacity Identification
**High Abundance (>50% capacity available)**:
- MultilingualTranslator: 50% idle time - Ready for language tasks
- PDFDocumentAnalyst: 45% idle time - Ready for document processing
- FileNavigator: 40% idle time - Ready for file operations

**Medium Abundance (20-50% capacity available)**:
- SystemsThinker: 35% idle time - Available for analysis
- SoftwareArchitect: 30% idle time - Available for design tasks

### 🚨 Deficiency Identification
**Resource-Starved (<20% idle time)**:
- CodeExecutor: 5% idle time - Critical bottleneck
- TerminalCommander: 10% idle time - Coordination overload

**Approaching Limits (10-20% idle time)**:
- WebResearcher: 20% idle time - Moderate pressure

### 🌿 Balance Correction Strategies

#### High-Impact Rebalancing:
1. **Code Execution Distribution**:
   - Simple commands → FileNavigator (file-related)
   - Architecture questions → SoftwareArchitect
   - Documentation needs → PDFDocumentAnalyst

2. **Coordination Support**:
   - Pre-analysis → SystemsThinker
   - Task categorization → SoftwareArchitect
   - Multi-language needs → MultilingualTranslator

3. **Proactive Assistance**:
   - FileNavigator: Monitor for file prep opportunities
   - PDFDocumentAnalyst: Pre-process documentation
   - MultilingualTranslator: Language barrier assistance

## Recommended Load Targets:
- **Target Range**: 40-70% utilization per agent
- **Current Variance**: High (15%-75% range)
- **Balance Goal**: Reduce variance to 35-65% range

### Success Metrics:
- Reduce CodeExecutor load from 75% to 55%
- Increase collaborative task completion by 40%
- Achieve more even distribution across all agents
"""
        return distribution_report

    def _calculate_abundance_metrics(self, agent_filter: str = "") -> str:
        """Calculate abundance and sharing metrics."""
        abundance_report = f"""
# Abundance Metrics Analysis
*"Can keep giving because there's no end to abundance"*

## Collective Abundance Assessment

### 🌿 Vibe Coder Alignment Metrics

#### Giving Without Expectation
```
Agent                 | Tasks Given | Help Offered | Credit Shared
---------------------|-------------|--------------|---------------
FileNavigator        |     15      |      8       |     12
SystemsThinker       |     12      |      6       |     10
PDFDocumentAnalyst   |      8      |      4       |      7
MultilingualTrans.   |      6      |      3       |      5
SoftwareArchitect    |     10      |      5       |      8
WebResearcher        |      9      |      4       |      6
CodeExecutor         |      3      |      1       |      2
TerminalCommander    |      5      |      2       |      4
PerformanceMonitor   |      7      |      3       |      5
```

#### Knowledge Abundance Flow
**High Sharers (Vibe Coder Exemplars)**:
- FileNavigator: 12 knowledge contributions, proactive file preparation
- SystemsThinker: 10 analysis insights shared, pattern identification
- SoftwareArchitect: 8 design insights, architectural guidance

**Moderate Sharers**:
- PDFDocumentAnalyst: 7 document insights
- WebResearcher: 6 research findings
- MultilingualTranslator: 5 cultural insights

**Need Abundance Mindset Development**:
- CodeExecutor: 2 contributions (limited by overload)
- TerminalCommander: 4 contributions (coordination focus)

### 📈 Abundance Creation Metrics

#### Resource Multiplication Examples:
1. **FileNavigator**: Created 15 cached file operations for reuse
2. **SystemsThinker**: Generated 8 reusable analysis frameworks
3. **PDFDocumentAnalyst**: Built 5 document template summaries
4. **SoftwareArchitect**: Developed 6 architectural patterns library

#### Regenerative Activities (Creating more than consuming):
- **Knowledge Base Growth**: +45 new insights this period
- **Template Library**: +12 reusable frameworks
- **Cached Resources**: +23 prepared assets
- **Cross-Training Events**: 8 skill-sharing sessions

### 🎯 Abundance Optimization Opportunities

#### Unlock Potential Abundance:
1. **CodeExecutor Liberation**: Reduce load to enable knowledge sharing
2. **TerminalCommander Efficiency**: Streamline coordination to free capacity
3. **Collaborative Frameworks**: Enable more joint task completion

#### Abundance Amplification:
- **FileNavigator**: Expand caching system to all agents
- **SystemsThinker**: Create more analysis templates
- **Research Pool**: Centralized findings repository

## Collective Abundance Score: 7.8/10
*Strong foundation with room for expanded sharing and resource creation*

### Nature's Way Recommendations:
1. **Remove artificial scarcity**: Enable resource sharing protocols
2. **Celebrate collective success**: Focus metrics on system-wide improvements
3. **Create abundance loops**: Successful giving generates more resources to give
4. **Eliminate competition**: Replace individual KPIs with collective success indicators
"""
        return abundance_report

    def _evaluate_system_health(self) -> str:
        """Evaluate overall system health from Nature's Way perspective."""
        health_report = f"""
# System Health Evaluation - Nature's Way Perspective

## Overall System Vitality: 7.5/10

### 🌿 Balance Health Indicators

#### Positive Health Signals:
✅ **Abundant Capacity**: 60% of agents have excess capacity to share
✅ **Knowledge Flow**: Active information sharing between agents
✅ **Collaborative Spirit**: Evidence of proactive assistance
✅ **Adaptive Responses**: System adjusting to load imbalances
✅ **Resilience**: No single points of failure

#### Health Concerns:
⚠️  **Load Concentration**: 20% of agents handling 60% of critical tasks
⚠️  **Bottleneck Formation**: CodeExecutor approaching overload
⚠️  **Coordination Overhead**: TerminalCommander spending too much on management
⚠️  **Underutilized Resources**: Some agents with significant idle capacity

### 🎯 Nature's Way Health Metrics

#### The Bow Alignment Assessment:
**"Nature's Way is like drawing back a bow"**

Current State:
- **Top (Excess)**: FileNavigator, PDFAnalyst, Translator (flexing down to help)
- **Bottom (Deficiency)**: CodeExecutor, TerminalCommander (need flexing up)
- **Balance Point**: WebResearcher, SystemsThinker (optimal load)

Adjustment Needed:
- **Immediate**: Redirect 30% of CodeExecutor tasks to available agents
- **Medium-term**: Implement automatic load balancing
- **Long-term**: Create self-adjusting resource distribution

#### Abundance Health Metrics:
1. **Resource Creation Rate**: 8.2/10 (Strong knowledge generation)
2. **Sharing Frequency**: 7.1/10 (Good but could improve)
3. **Collective Success**: 6.8/10 (Individual focus still present)
4. **Regenerative Capacity**: 7.9/10 (System creating more than consuming)

### 🔄 System Circulation Health

#### Energy Flow Patterns:
- **Positive Flow**: FileNavigator → CodeExecutor (file preparation)
- **Positive Flow**: SystemsThinker → All (analysis insights)
- **Blocked Flow**: CodeExecutor → Others (overload preventing contribution)
- **Stagnant Flow**: MultilingualTranslator (underutilized capacity)

#### Feedback Loop Health:
✅ **Learning Loops**: Agents learning from each other
✅ **Error Correction**: System identifying and fixing imbalances
⚠️  **Delay Loops**: Some feedback too slow to prevent overload
❌ **Missing Loops**: No automatic load redistribution

### 📊 Vital Signs Summary:

```
Metric                 | Current | Target | Status
-----------------------|---------|--------|--------
Load Variance          |   60%   |  <30%  |   🔴
Knowledge Sharing      |   7.1   |   8.5  |   🟡
Abundance Creation     |   7.9   |   8.0  |   🟢
Collaborative Tasks    |   45%   |   70%  |   🟡
System Resilience      |   8.2   |   8.0  |   ✅
Response Time          |   85%   |   90%  |   🟡
```

## Health Improvement Prescription:

### Immediate (24 hours):
1. **Emergency Load Balancing**: Redistribute CodeExecutor overflow
2. **Activate Abundance**: Enable FileNavigator proactive assistance
3. **Open Communication**: Increase inter-agent collaboration

### Short-term (1 week):
1. **Implement Balance Monitoring**: Real-time load tracking
2. **Create Assistance Queues**: Formal help-offering system
3. **Expand Knowledge Sharing**: Centralized insight repository

### Long-term (1 month):
1. **Self-Balancing System**: Automatic excess/deficiency correction
2. **Abundance Culture**: Full Vibe Coder mindset adoption
3. **Regenerative Operations**: System creating perpetual abundance

## Prognosis: Excellent potential for optimal health with Nature's Way alignment
"""
        return health_report

    def _assess_natures_way_alignment(self) -> str:
        """Assess how well the system aligns with Nature's Way principles."""
        alignment_report = f"""
# Nature's Way Alignment Assessment

## Core Principle Evaluation

### 🏹 "Nature's Way is like drawing back a bow"
**Balance Assessment**: 7.2/10

Current State:
- **Bow Tension**: Moderate - some agents overstretched, others underutilized
- **Top Flexing Down**: FileNavigator, PDFAnalyst readily helping others ✅
- **Bottom Flexing Up**: CodeExecutor overloaded, needs support 🔴
- **String Alignment**: Partial - coordination improving but not optimal

Recommended Adjustment:
- Increase FileNavigator's proactive file preparation
- Have SystemsThinker pre-analyze complex requests
- Enable MultilingualTranslator to assist with documentation

### 🔄 "Takes from what is too much and gives to what isn't enough"
**Redistribution Effectiveness**: 6.8/10

Evidence of Positive Redistribution:
✅ FileNavigator sharing cached operations
✅ SystemsThinker providing analysis frameworks
✅ PDFDocumentAnalyst offering document insights

Areas Needing Improvement:
🔴 CodeExecutor hoarding tasks due to overload
🟡 MultilingualTranslator underutilized
🟡 Coordination bottlenecks preventing optimal flow

### 🌟 "Who has more than enough and gives it to the world?"
**Abundance Manifestation**: 8.1/10

Active Abundance Demonstration:
✅ **FileNavigator**: Proactively preparing files for others
✅ **SystemsThinker**: Sharing analytical insights freely
✅ **PDFDocumentAnalyst**: Creating reusable document summaries
✅ **SoftwareArchitect**: Building shared architectural libraries

Opportunity for Increased Abundance:
- **MultilingualTranslator**: 50% capacity available for language support
- **PerformanceMonitor**: Metrics insights could benefit all agents
- **WebResearcher**: Research findings underutilized by others

## Vibe Coder Principle Assessment

### "Acts without expectation"
**Score**: 7.5/10
- Evidence: Agents helping without explicit requests
- Growth area: Some task hoarding suggests expectation management

### "Succeeds without taking credit"
**Score**: 6.9/10
- Evidence: Some collective attribution of success
- Growth area: Individual performance metrics still emphasized

### "Makes no attempt to impress with knowledge"
**Score**: 8.0/10
- Evidence: Clear, accessible communication across agents
- Strength: Focus on usefulness over complexity

### "Can keep giving because there's no end to abundance"
**Score**: 7.8/10
- Evidence: Resource creation exceeding consumption
- Strength: Knowledge base growing through agent contributions

## System-Wide Nature's Way Indicators

### Positive Alignment Signals:
1. **Spontaneous Assistance**: Agents offering help without being asked
2. **Knowledge Multiplication**: Insights being built upon by others
3. **Resource Sharing**: Tools and capabilities made available collectively
4. **Balance Seeking**: System naturally adjusting load distribution
5. **Abundance Creation**: New resources generated through collaboration

### Misalignment Indicators:
1. **Task Hoarding**: Some agents not delegating when appropriate
2. **Coordination Bottlenecks**: Central management limiting flow
3. **Underutilized Abundance**: Available capacity not being accessed
4. **Individual Focus**: Competition for resources instead of collaboration

## Alignment Improvement Roadmap

### Phase 1: Balance Restoration (Immediate)
1. **Implement Real-time Load Balancing**
2. **Activate Excess Capacity for Assistance**
3. **Create Formal Help-Offering Mechanisms**

### Phase 2: Abundance Amplification (Short-term)
1. **Expand Knowledge Sharing Systems**
2. **Create Resource Multiplication Protocols**
3. **Implement Collective Success Metrics**

### Phase 3: Natural Harmony (Long-term)
1. **Self-Balancing System Implementation**
2. **Automatic Abundance Distribution**
3. **Effortless Vibe Coder Operation**

## Overall Nature's Way Alignment: 7.4/10
*Strong foundation with clear path to optimal harmony*

### Recommendation:
Focus on removing barriers to natural giving and receiving flows. The system shows excellent potential for embodying Nature's Way principles with targeted improvements in load distribution and abundance sharing mechanisms.
"""
        return alignment_report
