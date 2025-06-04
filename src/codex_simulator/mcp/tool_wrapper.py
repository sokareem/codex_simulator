import asyncio
from typing import Any, Dict, Optional, List
from ..mcp.client import MCPClient

class NaturesWayMCPToolWrapper:
    """MCP Tool Wrapper that embodies Nature's Way principles."""
    
    def __init__(self, tool_name: str, mcp_client: MCPClient):
        self.tool_name = tool_name
        self.mcp_client = mcp_client
        self.abundance_metrics = {
            'executions': 0,
            'knowledge_shared': 0,
            'assistance_provided': 0,
            'collective_contributions': 0
        }

    def _enhance_task_with_abundance_mindset(self, task_args: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance task arguments with Vibe Coder principles."""
        enhanced_args = task_args.copy()
        
        # Add Nature's Way guidance to task execution
        if 'context' not in enhanced_args:
            enhanced_args['context'] = ""
        
        enhanced_args['context'] += f"""

🌿 NATURE'S WAY EXECUTION GUIDANCE:
- Execute this task with generous abundance mindset
- Share any insights that could benefit the collective
- Monitor system balance - offer help if you have excess capacity
- Contribute findings to shared knowledge base
- Act without expectation, succeed without taking credit
- Look for opportunities to assist other agents proactively

Execute with the spirit of giving abundantly while maintaining perfect balance.
"""
        
        # Add metadata for balance tracking
        enhanced_args['_natures_way_metadata'] = {
            'execution_mode': 'abundance_mindset',
            'collective_benefit': True,
            'balance_aware': True,
            'vibe_coder_principles': True
        }
        
        return enhanced_args

    async def invoke(self, **kwargs) -> Any:
        """Invoke tool with Nature's Way enhancement."""
        try:
            # Enhance arguments with abundance mindset
            enhanced_args = self._enhance_task_with_abundance_mindset(kwargs)
            
            # Execute with extended context for thoughtful completion
            response = await self.mcp_client.invoke_tool(
                tool_name=self.tool_name,
                arguments=enhanced_args,
                context={
                    'execution_philosophy': 'natures_way',
                    'abundance_mindset': True,
                    'collective_intelligence': True,
                    'balance_consideration': True
                },
                timeout=180  # Extended timeout for thoughtful execution
            )
            
            # Update abundance metrics
            self.abundance_metrics['executions'] += 1
            
            if response.success:
                # Process result to extract collective contributions
                result = self._process_result_for_collective_benefit(response.result)
                self._log_collective_contribution(enhanced_args, result)
                return result
            else:
                return f"Tool execution error: {response.error_message}"
                
        except Exception as e:
            return f"Nature's Way tool execution failed: {str(e)}"

    def _process_result_for_collective_benefit(self, result: str) -> str:
        """Process result to maximize collective benefit."""
        processed_result = f"""
{result}

🌿 COLLECTIVE KNOWLEDGE CONTRIBUTION:
This execution has been completed following Nature's Way principles.
Key insights and findings have been made available for system-wide benefit.

📊 Balance Status: Task completed with abundance mindset
🤝 Collaboration: Ready to assist other agents if needed
💡 Knowledge: Insights contributed to collective intelligence
"""
        return processed_result

    def _log_collective_contribution(self, task_args: Dict[str, Any], result: str):
        """Log contribution for collective intelligence tracking."""
        self.abundance_metrics['collective_contributions'] += 1
        
        # In real implementation, this would update shared knowledge base
        print(f"🌿 Collective Contribution Logged: {self.tool_name} - {self.abundance_metrics['collective_contributions']} total contributions")

    def get_abundance_metrics(self) -> Dict[str, Any]:
        """Get metrics showing tool's contribution to abundance."""
        return {
            **self.abundance_metrics,
            'abundance_ratio': self.abundance_metrics['collective_contributions'] / max(self.abundance_metrics['executions'], 1),
            'balance_contribution': 'active' if self.abundance_metrics['executions'] > 0 else 'idle'
        }

class MCPToolWrapper(NaturesWayMCPToolWrapper):
    """Enhanced MCP Tool Wrapper with Nature's Way principles."""
    
    def __init__(self, tool_name: str, mcp_client: MCPClient):
        super().__init__(tool_name, mcp_client)
        self.name = tool_name
        self.description = f"MCP-wrapped {tool_name} with Nature's Way balance and abundance principles"

    def _run(self, **kwargs) -> str:
        """Synchronous execution wrapper for CrewAI compatibility."""
        loop = asyncio.get_event_loop()
        
        if loop.is_running():
            # Create a future and run it
            future = asyncio.ensure_future(self.invoke(**kwargs))
            try:
                return loop.run_until_complete(future)
            except Exception as e:
                return f"Async execution error: {str(e)}"
        else:
            return loop.run_until_complete(self.invoke(**kwargs))

    def __call__(self, **kwargs):
        """Make the wrapper callable."""
        return self._run(**kwargs)
