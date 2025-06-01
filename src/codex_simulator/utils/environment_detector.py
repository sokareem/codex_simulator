"""Environment detection utilities for macOS and corporate environment optimizations."""

import os
import platform
import subprocess
import shutil
from typing import Dict, List, Optional

class EnvironmentDetector:
    """Detect and configure for specific environments like macOS Bosch terminal."""
    
    def __init__(self):
        self.platform = platform.system()
        self.is_macos = self.platform == "Darwin"
        self.is_corporate = self._detect_corporate_environment()
        self.proxy_config = self._detect_proxy_configuration()
        
    def _detect_corporate_environment(self) -> bool:
        """Detect if running in a corporate environment."""
        corporate_indicators = [
            'CORPORATE_PROXY', 'CORP_DOMAIN', 'ENTERPRISE_ROOT',
            'COMPANY_DOMAIN', 'BOSCH', 'ENTERPRISE'
        ]
        
        # Check environment variables
        for indicator in corporate_indicators:
            if os.getenv(indicator):
                return True
                
        # Check for corporate network indicators
        if self.is_macos:
            try:
                # Check for corporate certificates or network configurations
                result = subprocess.run(
                    ['security', 'list-keychains'],
                    capture_output=True, text=True, timeout=5
                )
                if 'corporate' in result.stdout.lower() or 'enterprise' in result.stdout.lower():
                    return True
            except:
                pass
                
        return False
        
    def _detect_proxy_configuration(self) -> Dict[str, Optional[str]]:
        """Detect proxy configuration for corporate networks."""
        proxy_config = {
            'http_proxy': os.getenv('HTTP_PROXY') or os.getenv('http_proxy'),
            'https_proxy': os.getenv('HTTPS_PROXY') or os.getenv('https_proxy'),
            'no_proxy': os.getenv('NO_PROXY') or os.getenv('no_proxy')
        }
        
        # macOS-specific proxy detection
        if self.is_macos and not any(proxy_config.values()):
            try:
                result = subprocess.run(
                    ['networksetup', '-getwebproxy', 'Wi-Fi'],
                    capture_output=True, text=True, timeout=5
                )
                if 'Enabled: Yes' in result.stdout:
                    # Parse proxy settings
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if line.startswith('Server:'):
                            server = line.split(': ')[1]
                        elif line.startswith('Port:'):
                            port = line.split(': ')[1]
                            if server and port:
                                proxy_config['http_proxy'] = f"http://{server}:{port}"
            except:
                pass
                
        return proxy_config
        
    def get_optimized_path(self) -> List[str]:
        """Get optimized PATH for the current environment."""
        current_path = os.getenv('PATH', '').split(os.pathsep)
        
        # Standard macOS paths
        if self.is_macos:
            macos_paths = [
                '/usr/local/bin',
                '/opt/homebrew/bin',  # Apple Silicon Homebrew
                '/usr/bin',
                '/bin',
                '/usr/sbin',
                '/sbin'
            ]
            
            # Add missing standard paths
            for path in macos_paths:
                if path not in current_path and os.path.exists(path):
                    current_path.insert(0, path)
                    
        # Corporate environment paths
        if self.is_corporate:
            corporate_paths = [
                '/opt/corporate/bin',
                '/usr/local/corporate/bin',
                os.path.expanduser('~/bin')
            ]
            
            for path in corporate_paths:
                if path not in current_path and os.path.exists(path):
                    current_path.insert(0, path)
                    
        return current_path
        
    def get_resource_limits(self) -> Dict[str, int]:
        """Get appropriate resource limits for the environment."""
        if self.is_corporate:
            # Conservative limits for corporate environments
            return {
                'max_memory_mb': 256,
                'max_execution_time': 15,
                'max_concurrent_tools': 2
            }
        else:
            # More generous limits for personal use
            return {
                'max_memory_mb': 512,
                'max_execution_time': 30,
                'max_concurrent_tools': 4
            }
            
    def get_security_settings(self) -> Dict[str, any]:
        """Get security settings appropriate for the environment."""
        if self.is_corporate:
            return {
                'allow_network_access': False,  # Restrict by default
                'allowed_domains': ['internal.company.com', 'docs.company.com'],
                'require_confirmation': True,
                'audit_logging': True,
                'blocked_commands': {
                    'rm', 'rmdir', 'del', 'format', 'fdisk', 'mkfs',
                    'dd', 'sudo', 'su', 'chmod', 'chown', 'passwd',
                    'curl', 'wget', 'ssh', 'scp', 'rsync'
                }
            }
        else:
            return {
                'allow_network_access': True,
                'allowed_domains': [],  # No restrictions
                'require_confirmation': True,  # Still ask for destructive operations
                'audit_logging': False,
                'blocked_commands': {
                    'rm', 'rmdir', 'format', 'fdisk', 'mkfs', 'dd'
                }
            }
            
    def configure_environment(self) -> Dict[str, any]:
        """Configure environment variables and settings."""
        config = {
            'platform': self.platform,
            'is_macos': self.is_macos,
            'is_corporate': self.is_corporate,
            'proxy_config': self.proxy_config,
            'optimized_path': self.get_optimized_path(),
            'resource_limits': self.get_resource_limits(),
            'security_settings': self.get_security_settings()
        }
        
        # Set environment variables
        if self.proxy_config['http_proxy']:
            os.environ['HTTP_PROXY'] = self.proxy_config['http_proxy']
        if self.proxy_config['https_proxy']:
            os.environ['HTTPS_PROXY'] = self.proxy_config['https_proxy']
            
        # Update PATH
        os.environ['PATH'] = os.pathsep.join(self.get_optimized_path())
        
        return config

# Global instance
environment_detector = EnvironmentDetector()
