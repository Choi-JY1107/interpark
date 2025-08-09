from typing import Dict, Any, Type
import logging

logger = logging.getLogger(__name__)


class DIContainer:
    """간단한 의존성 주입 컨테이너"""
    
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Any] = {}
        
    def register(self, interface: Type, implementation: Any = None, factory: Any = None):
        """서비스 등록"""
        if implementation:
            self._services[interface] = implementation
        elif factory:
            self._factories[interface] = factory
        else:
            raise ValueError("Implementation or factory must be provided")
            
    def resolve(self, interface: Type) -> Any:
        """서비스 해결"""
        if interface in self._services:
            return self._services[interface]
            
        if interface in self._factories:
            instance = self._factories[interface]()
            self._services[interface] = instance
            return instance
            
        raise ValueError(f"Service {interface} not registered")
        
    def clear(self):
        """컨테이너 초기화"""
        self._services.clear()
        self._factories.clear()


container = DIContainer()