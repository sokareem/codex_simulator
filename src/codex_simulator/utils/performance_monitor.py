"""Performance monitoring utilities for tracking tool execution and system resources."""

import time
import asyncio
import logging
from typing import Dict, Any, Optional
from functools import wraps
from contextlib import asynccontextmanager

# Try to import psutil, but gracefully handle if it's not available
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    # Create a mock psutil for basic functionality
    class MockPsutil:
        class Process:
            def memory_info(self):
                class MemInfo:
                    rss = 0
                return MemInfo()
        
        @staticmethod
        def cpu_percent(interval=1):
            return 0.0
            
        @staticmethod
        def virtual_memory():
            class VirtMem:
                percent = 0.0
            return VirtMem()
            
        @staticmethod
        def disk_usage(path):
            class DiskUsage:
                percent = 0.0
            return DiskUsage()
            
        @staticmethod
        def getloadavg():
            return (0.0, 0.0, 0.0)
            
        @staticmethod
        def pids():
            return []
    
    psutil = MockPsutil()

class PerformanceMonitor:
    """Monitor tool execution performance and system resources."""
    
    def __init__(self):
        self.execution_stats = {}
        self.logger = logging.getLogger(__name__)
        self.psutil_available = PSUTIL_AVAILABLE
        
        if not self.psutil_available:
            self.logger.warning("psutil not available - performance monitoring will be limited")
        
    def track_execution(self, tool_name: str):
        """Decorator to track tool execution performance."""
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = 0
                
                if self.psutil_available:
                    try:
                        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                    except:
                        start_memory = 0
                
                try:
                    result = await func(*args, **kwargs)
                    success = True
                    error = None
                except Exception as e:
                    result = None
                    success = False
                    error = str(e)
                    raise
                finally:
                    end_time = time.time()
                    end_memory = 0
                    
                    if self.psutil_available:
                        try:
                            end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                        except:
                            end_memory = start_memory
                    
                    stats = {
                        'execution_time': end_time - start_time,
                        'memory_used': end_memory - start_memory,
                        'success': success,
                        'error': error,
                        'timestamp': time.time()
                    }
                    
                    self._record_stats(tool_name, stats)
                    
                return result
                
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                start_memory = 0
                
                if self.psutil_available:
                    try:
                        start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                    except:
                        start_memory = 0
                
                try:
                    result = func(*args, **kwargs)
                    success = True
                    error = None
                except Exception as e:
                    result = None
                    success = False
                    error = str(e)
                    raise
                finally:
                    end_time = time.time()
                    end_memory = 0
                    
                    if self.psutil_available:
                        try:
                            end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                        except:
                            end_memory = start_memory
                    
                    stats = {
                        'execution_time': end_time - start_time,
                        'memory_used': end_memory - start_memory,
                        'success': success,
                        'error': error,
                        'timestamp': time.time()
                    }
                    
                    self._record_stats(tool_name, stats)
                    
                return result
                
            # Return appropriate wrapper based on function type
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return sync_wrapper
                
        return decorator
        
    def _record_stats(self, tool_name: str, stats: Dict[str, Any]):
        """Record execution statistics for a tool."""
        if tool_name not in self.execution_stats:
            self.execution_stats[tool_name] = []
            
        self.execution_stats[tool_name].append(stats)
        
        # Log performance metrics
        memory_info = f", Memory: {stats['memory_used']:.2f}MB" if self.psutil_available else ""
        self.logger.info(
            f"Tool: {tool_name}, "
            f"Time: {stats['execution_time']:.2f}s"
            f"{memory_info}, "
            f"Success: {stats['success']}"
        )
        
        # Keep only last 100 executions per tool
        if len(self.execution_stats[tool_name]) > 100:
            self.execution_stats[tool_name] = self.execution_stats[tool_name][-100:]
            
    def get_tool_stats(self, tool_name: str) -> Dict[str, Any]:
        """Get aggregated statistics for a specific tool."""
        if tool_name not in self.execution_stats:
            return {}
            
        stats = self.execution_stats[tool_name]
        if not stats:
            return {}
            
        successful_stats = [s for s in stats if s['success']]
        
        if not successful_stats:
            return {
                'total_executions': len(stats),
                'success_rate': 0.0,
                'avg_execution_time': 0.0,
                'avg_memory_used': 0.0
            }
            
        return {
            'total_executions': len(stats),
            'success_rate': len(successful_stats) / len(stats),
            'avg_execution_time': sum(s['execution_time'] for s in successful_stats) / len(successful_stats),
            'avg_memory_used': sum(s['memory_used'] for s in successful_stats) / len(successful_stats),
            'min_execution_time': min(s['execution_time'] for s in successful_stats),
            'max_execution_time': max(s['execution_time'] for s in successful_stats)
        }
        
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system resource status."""
        if not self.psutil_available:
            return {
                'cpu_percent': 'N/A (psutil not available)',
                'memory_percent': 'N/A (psutil not available)', 
                'disk_percent': 'N/A (psutil not available)',
                'load_average': 'N/A (psutil not available)',
                'process_count': 'N/A (psutil not available)'
            }
        
        try:
            return {
                'cpu_percent': psutil.cpu_percent(interval=1),
                'memory_percent': psutil.virtual_memory().percent,
                'disk_percent': psutil.disk_usage('/').percent,
                'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None,
                'process_count': len(psutil.pids())
            }
        except Exception as e:
            return {
                'cpu_percent': f'Error: {e}',
                'memory_percent': f'Error: {e}',
                'disk_percent': f'Error: {e}',
                'load_average': f'Error: {e}',
                'process_count': f'Error: {e}'
            }
        
    @asynccontextmanager
    async def monitor_context(self, operation_name: str):
        """Context manager for monitoring specific operations."""
        start_time = time.time()
        start_memory = 0
        
        if self.psutil_available:
            try:
                start_memory = psutil.Process().memory_info().rss / 1024 / 1024
            except:
                start_memory = 0
        
        try:
            yield
        finally:
            end_time = time.time()
            end_memory = start_memory
            
            if self.psutil_available:
                try:
                    end_memory = psutil.Process().memory_info().rss / 1024 / 1024
                except:
                    pass
            
            memory_info = f", memory change: {end_memory - start_memory:.2f}MB" if self.psutil_available else ""
            self.logger.info(
                f"Operation '{operation_name}' completed in "
                f"{end_time - start_time:.2f}s"
                f"{memory_info}"
            )

# Global instance
performance_monitor = PerformanceMonitor()
