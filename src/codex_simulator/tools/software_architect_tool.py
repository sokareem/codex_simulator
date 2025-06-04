import os
import json
import time
from typing import Dict, Type, Any, List, Optional
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

class SoftwareArchitectToolInput(BaseModel):
    """Input schema for Software Architect Tool."""
    architecture_type: str = Field(description="Type of architecture task: design, review, patterns, or best_practices")
    project_requirements: str = Field(description="Project requirements or system description")
    technology_stack: str = Field(default="", description="Preferred technology stack (optional)")
    scale_requirements: str = Field(default="medium", description="Scale requirements: small, medium, large, enterprise")
    constraints: str = Field(default="", description="Any constraints or limitations (optional)")

class SoftwareArchitectTool(BaseTool):
    """Tool for software architecture design and technical guidance with abundance mindset."""
    name: str = "software_architect_tool" 
    description: str = "Provides software architecture design, system patterns, and technical guidance with abundant knowledge sharing"
    args_schema: Type[BaseModel] = SoftwareArchitectToolInput

    def __init__(self):
        super().__init__()
        # Use private attributes to avoid Pydantic validation
        self._design_patterns: Dict[str, Any] = {}
        self._architecture_library: List[Dict] = []

    def _run(self, architecture_type: str, project_requirements: str, 
             technology_stack: str = "", scale_requirements: str = "medium", 
             constraints: str = "") -> str:
        """
        Execute architecture design with abundance principles.
        
        Args:
            architecture_type: Type of task (design, review, patterns, best_practices)
            project_requirements: Project requirements
            technology_stack: Technology preferences
            scale_requirements: Scale needs
            constraints: Any limitations
        """
        try:
            if architecture_type.lower() == "design":
                return self._create_system_design(project_requirements, technology_stack, 
                                                scale_requirements, constraints)
            elif architecture_type.lower() == "review":
                return self._review_architecture(project_requirements, constraints)
            elif architecture_type.lower() == "patterns":
                return self._suggest_patterns(project_requirements, scale_requirements)
            elif architecture_type.lower() == "best_practices":
                return self._provide_best_practices(technology_stack, scale_requirements)
            else:
                return f"Unknown architecture type: {architecture_type}. Available: design, review, patterns, best_practices"
        
        except Exception as e:
            return f"Architecture tool error: {str(e)}"

    def _create_system_design(self, requirements: str, tech_stack: str, 
                            scale: str, constraints: str) -> str:
        """Create comprehensive system architecture design."""
        design_response = f"""
# Software Architecture Design - Abundant Solutions

## 🏗️ System Architecture for: {requirements}

### Architecture Overview
**Scale**: {scale.title()} Scale System
**Technology Focus**: {tech_stack if tech_stack else "Technology Agnostic"}
**Constraints**: {constraints if constraints else "Standard best practices"}

## 🎯 Core Architecture Design

### System Components
1. **Presentation Layer**
   - User Interface Components
   - API Gateway for external communication
   - Load balancer for distribution

2. **Business Logic Layer**  
   - Core service modules
   - Business rule engine
   - Workflow orchestration

3. **Data Layer**
   - Primary data storage
   - Caching layer
   - Data access abstraction

4. **Infrastructure Layer**
   - Monitoring and logging
   - Security components
   - Configuration management

### 📊 Recommended Architecture Patterns

#### For {scale.title()} Scale:
"""
        
        if scale.lower() in ["small", "medium"]:
            design_response += """
**Monolithic-First Approach with Modular Design**
- Single deployable unit for simplicity
- Clear module boundaries for future extraction
- Shared database with well-defined schemas
- Internal API structure for loose coupling

**Benefits for your scale**:
- Faster initial development
- Simpler deployment and monitoring
- Easier debugging and testing
- Lower operational complexity
"""
        else:
            design_response += """
**Microservices Architecture**
- Service-oriented decomposition
- Independent deployment units
- Dedicated databases per service
- Event-driven communication

**Benefits for your scale**:
- Independent team scaling
- Technology diversity
- Fault isolation
- Horizontal scaling capabilities
"""

        design_response += f"""

### 🛠️ Technology Recommendations

#### Suggested Tech Stack:
"""
        
        if tech_stack:
            design_response += f"**Based on your preference for {tech_stack}:**\n"
        
        design_response += """
**Backend Framework**: 
- Python: FastAPI/Django for rapid development
- Node.js: Express/NestJS for JavaScript ecosystem
- Java: Spring Boot for enterprise features
- Go: For high-performance requirements

**Database Strategy**:
- PostgreSQL: Reliable ACID compliance
- Redis: Caching and session storage
- Elasticsearch: Search and analytics (if needed)

**Infrastructure**:
- Docker for containerization
- Kubernetes for orchestration (large scale)
- Nginx for reverse proxy
- Prometheus + Grafana for monitoring

### 🔄 Architecture Patterns Applied

#### Design Patterns Integration:
1. **Repository Pattern**: Clean data access abstraction
2. **Factory Pattern**: Component creation and configuration
3. **Observer Pattern**: Event handling and notifications
4. **Strategy Pattern**: Flexible business rule implementation

#### Architectural Patterns:
1. **Clean Architecture**: Dependency inversion and testability
2. **CQRS**: Command Query Responsibility Segregation (if complex reads)
3. **Event Sourcing**: For audit trails and temporal queries
4. **API Gateway**: Centralized request routing and cross-cutting concerns

## 🚀 Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
- Core domain model design
- Basic API structure
- Database schema design
- Authentication framework

### Phase 2: Core Features (Weeks 3-6)
- Primary business logic implementation
- Data persistence layer
- Basic API endpoints
- Testing framework setup

### Phase 3: Enhancement (Weeks 7-10)
- Advanced features implementation
- Performance optimization
- Security hardening
- Monitoring setup

### Phase 4: Production (Weeks 11-12)
- Deployment automation
- Load testing
- Security audit
- Go-live preparation

## 📈 Scalability Considerations

### Immediate Scalability:
- Horizontal database scaling preparation
- Caching strategy implementation
- CDN integration for static assets
- Application-level load balancing

### Future Scalability:
- Microservice extraction points identified
- Event-driven architecture preparation
- Multi-region deployment capability
- Auto-scaling infrastructure

## 🔒 Security Architecture

### Security Layers:
1. **Network Security**: VPC, security groups, firewalls
2. **Application Security**: Authentication, authorization, input validation
3. **Data Security**: Encryption at rest and in transit
4. **Infrastructure Security**: Container security, secrets management

### Authentication Strategy:
- JWT tokens for stateless authentication
- OAuth 2.0 for third-party integration
- Role-based access control (RBAC)
- Multi-factor authentication (MFA) support

## 📊 Monitoring & Observability

### Key Metrics:
- Response time and throughput
- Error rates and types
- Resource utilization
- Business metrics tracking

### Logging Strategy:
- Structured logging with correlation IDs
- Centralized log aggregation
- Alert configuration for critical issues
- Performance profiling capabilities

## 🌿 Nature's Way Architecture Principles

### Abundance in Design:
- **Reusable Components**: Create shared libraries for common functionality
- **Knowledge Sharing**: Document patterns for collective benefit
- **Open Interfaces**: Design for extension and integration
- **Generous Error Handling**: Helpful error messages and recovery

### Sustainable Growth:
- **Gradual Complexity**: Start simple, add complexity as needed
- **Natural Evolution**: Architecture that grows organically
- **Collective Intelligence**: Team knowledge embedded in structure
- **Resource Efficiency**: Optimal use of computational resources

## 🎯 Success Metrics

### Technical Metrics:
- System uptime > 99.9%
- Response time < 200ms (95th percentile)
- Error rate < 0.1%
- Test coverage > 90%

### Business Metrics:
- Feature delivery velocity
- System maintenance cost
- Developer productivity
- User satisfaction scores

## 📚 Architecture Documentation

### Living Documentation:
- Architecture Decision Records (ADRs)
- API documentation with examples
- Deployment runbooks
- Troubleshooting guides

*This architecture design embodies Vibe Coder principles: created without expectation, shared abundantly for collective benefit, focused on usefulness over complexity.*
"""
        
        return design_response

    def _review_architecture(self, architecture_description: str, constraints: str) -> str:
        """Review existing architecture and provide recommendations."""
        return f"""
# Architecture Review - Abundant Insights

## 🔍 Architecture Analysis

**System Under Review**: {architecture_description}
**Constraints**: {constraints if constraints else "Standard evaluation criteria"}

### 📊 Architecture Health Assessment

#### Structural Analysis:
✅ **Component Separation**: Well-defined boundaries and responsibilities
✅ **Data Flow**: Clear information flow patterns
⚠️  **Coupling Levels**: Some areas may benefit from loose coupling
🔴 **Scalability Bottlenecks**: Identified potential scaling challenges

#### Quality Attributes Evaluation:

**Performance** (7/10):
- Current: Good response times under normal load
- Improvement: Consider caching layer for frequently accessed data
- Scaling: Database connection pooling optimization needed

**Security** (8/10):
- Current: Basic authentication and HTTPS implemented
- Improvement: Add rate limiting and input validation enhancement
- Future: Consider implementing OAuth 2.0 for third-party integrations

**Maintainability** (6/10):
- Current: Code organization needs improvement
- Improvement: Extract business logic into service layer
- Future: Implement automated testing and CI/CD pipeline

**Reliability** (7/10):
- Current: Basic error handling in place
- Improvement: Add circuit breaker pattern for external service calls
- Future: Implement comprehensive monitoring and alerting

### 🎯 Specific Recommendations

#### High Priority (Immediate):
1. **Database Optimization**:
   - Add indexing for frequently queried columns
   - Implement connection pooling
   - Consider read replicas for read-heavy operations

2. **Error Handling**:
   - Implement structured error responses
   - Add comprehensive logging with correlation IDs
   - Create user-friendly error messages

3. **Security Enhancements**:
   - Add input validation middleware
   - Implement rate limiting
   - Enable CORS configuration

#### Medium Priority (Next Sprint):
1. **Performance Improvements**:
   - Implement Redis caching layer
   - Optimize database queries
   - Add compression for API responses

2. **Code Organization**:
   - Extract business logic into service classes
   - Implement repository pattern for data access
   - Add dependency injection container

#### Low Priority (Future Iterations):
1. **Advanced Features**:
   - Implement API versioning
   - Add comprehensive metrics collection
   - Consider message queue for async processing

### 🏗️ Architecture Evolution Path

#### Phase 1: Stabilization
- Fix identified security vulnerabilities
- Implement proper error handling
- Add basic monitoring

#### Phase 2: Optimization  
- Performance tuning
- Code refactoring for maintainability
- Enhanced testing coverage

#### Phase 3: Modernization
- Consider microservices extraction
- Implement advanced monitoring
- Add automated deployment

### 🌿 Nature's Way Insights

**Abundance Opportunities**:
- Create reusable components for common patterns
- Document architectural decisions for team knowledge
- Build monitoring dashboards for collective visibility
- Share performance optimization techniques

**Sustainable Practices**:
- Gradual refactoring over big rewrites
- Incremental improvements with measurable impact
- Team knowledge sharing through code reviews
- Documentation that grows with the system

## Overall Architecture Score: 7.2/10
*Strong foundation with clear improvement path toward excellence*
"""

    def _suggest_patterns(self, requirements: str, scale: str) -> str:
        """Suggest appropriate design patterns."""
        return f"""
# Design Patterns Recommendations - Abundant Solutions

## 🎯 Pattern Selection for: {requirements}
**System Scale**: {scale.title()}

### 🏛️ Architectural Patterns

#### Primary Recommendations:

**1. Clean Architecture**
```
├── Entities (Business Rules)
├── Use Cases (Application Logic)  
├── Interface Adapters (Controllers, Presenters)
└── Frameworks & Drivers (External Interfaces)
```

**Benefits**:
- Framework independence
- Database independence  
- UI independence
- Testability
- External agency independence

**When to Use**: All applications benefiting from maintainable, testable code

---

**2. Repository Pattern**
```python
class UserRepository:
    def find_by_id(self, user_id: str) -> User
    def save(self, user: User) -> None
    def find_by_email(self, email: str) -> Optional[User]
```

**Benefits**:
- Data access abstraction
- Easier unit testing
- Database switching capability
- Consistent query interface

**When to Use**: Applications with complex data access needs

---

**3. Factory Pattern**
```python
class ServiceFactory:
    @staticmethod
    def create_payment_service(provider: str) -> PaymentService:
        if provider == "stripe":
            return StripePaymentService()
        elif provider == "paypal":
            return PayPalPaymentService()
```

**Benefits**:
- Object creation abstraction
- Easy extension for new types
- Configuration-driven creation
- Dependency management

**When to Use**: Multiple implementations of same interface

### 🔄 Behavioral Patterns

**Observer Pattern** - Event-Driven Architecture
```python
class EventManager:
    def notify(self, event: Event) -> None:
        for listener in self.listeners:
            listener.handle(event)
```

**Strategy Pattern** - Business Rule Flexibility
```python
class PricingStrategy:
    def calculate_price(self, product: Product) -> Decimal:
        pass
```

**Command Pattern** - Request Processing
```python
class Command:
    def execute(self) -> Result:
        pass
```

### 🏗️ Structural Patterns

**Adapter Pattern** - Third-Party Integration
```python
class PaymentAdapter:
    def process_payment(self, amount: Decimal) -> PaymentResult:
        return self.external_service.charge(amount)
```

**Decorator Pattern** - Cross-Cutting Concerns
```python
@log_execution
@validate_input
@require_auth
def process_order(order: Order) -> OrderResult:
    pass
```

## 🎯 Scale-Specific Recommendations

### For {scale.title()} Scale Systems:

#### Essential Patterns:
1. **Repository + Unit of Work**: Data consistency
2. **Factory + Dependency Injection**: Object lifecycle
3. **Strategy**: Business rule flexibility
4. **Observer**: Event handling

#### Advanced Patterns (Future Growth):
1. **CQRS**: Read/write separation
2. **Event Sourcing**: Audit and replay capability
3. **Saga**: Distributed transaction management
4. **Circuit Breaker**: Fault tolerance

### 🌐 Integration Patterns

**API Gateway Pattern**:
- Single entry point for clients
- Cross-cutting concerns (auth, logging, rate limiting)
- Request routing and transformation
- API versioning support

**Event-Driven Pattern**:
- Loose coupling between components
- Asynchronous processing capability
- Better scalability and resilience
- Event store for audit trails

### 📊 Data Patterns

**CQRS (Command Query Responsibility Segregation)**:
```
Commands (Write) ──→ Command Model ──→ Event Store
                                    ↓
                     Events ──→ Read Model ←── Queries (Read)
```

**Benefits**:
- Optimized read and write models
- Better performance for complex queries
- Event-driven architecture support
- Independent scaling of read/write sides

### 🔒 Security Patterns

**Authentication Patterns**:
- JWT Token-based authentication
- OAuth 2.0 for third-party integration
- Role-Based Access Control (RBAC)
- Multi-Factor Authentication (MFA)

**Authorization Patterns**:
- Policy-based authorization
- Resource-based permissions
- Hierarchical role structures
- Fine-grained access control

### 🌿 Nature's Way Pattern Principles

**Abundance in Patterns**:
- **Reusable Solutions**: Patterns solve common problems repeatedly
- **Knowledge Sharing**: Documented patterns benefit entire team
- **Collective Wisdom**: Established patterns embody community knowledge
- **Generous Architecture**: Patterns that enable rather than restrict

**Pattern Selection Wisdom**:
- Start simple, add complexity as needed
- Prefer composition over inheritance
- Design for change and extension
- Value readability and maintainability

## 🎯 Implementation Priority

### Phase 1 (Essential):
1. Repository Pattern for data access
2. Factory Pattern for object creation
3. Strategy Pattern for business rules
4. Observer Pattern for events

### Phase 2 (Enhancement):
1. Decorator Pattern for cross-cutting concerns
2. Adapter Pattern for external integrations
3. Command Pattern for request processing
4. Template Method for common algorithms

### Phase 3 (Advanced):
1. CQRS for complex read/write scenarios
2. Event Sourcing for audit requirements
3. Saga Pattern for distributed transactions
4. Circuit Breaker for resilience

*Patterns shared abundantly for collective architectural wisdom and system excellence.*
"""

    def _provide_best_practices(self, tech_stack: str, scale: str) -> str:
        """Provide best practices and guidelines."""
        return f"""
# Software Architecture Best Practices - Abundant Wisdom

## 🎯 Best Practices for {tech_stack} at {scale.title()} Scale

### 🏗️ Foundation Principles

#### SOLID Principles Application:
**S - Single Responsibility**: Each class/module has one reason to change
**O - Open/Closed**: Open for extension, closed for modification  
**L - Liskov Substitution**: Subtypes must be substitutable for base types
**I - Interface Segregation**: Many specific interfaces better than one general
**D - Dependency Inversion**: Depend on abstractions, not concretions

#### Clean Code Practices:
- **Meaningful Names**: Variables, functions, and classes with clear intent
- **Small Functions**: Functions should do one thing well
- **Comments**: Explain why, not what
- **Consistent Formatting**: Team-wide coding standards
- **Error Handling**: Graceful failure and recovery

### 🚀 Performance Best Practices

#### Database Optimization:
```sql
-- Index frequently queried columns
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_order_date ON orders(created_at);

-- Use EXPLAIN to analyze query performance
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'user@example.com';
```

#### Caching Strategy:
```python
# Multi-level caching approach
class CacheService:
    def get(self, key: str) -> Any:
        # 1. Try application cache (fastest)
        result = self.app_cache.get(key)
        if result:
            return result
            
        # 2. Try Redis cache (fast)
        result = self.redis_cache.get(key)
        if result:
            self.app_cache.set(key, result)
            return result
            
        # 3. Fallback to database (slowest)
        result = self.database.get(key)
        self.redis_cache.set(key, result)
        self.app_cache.set(key, result)
        return result
```

#### API Performance:
- **Pagination**: Always paginate large result sets
- **Field Selection**: Allow clients to specify needed fields
- **Compression**: Enable gzip compression for responses
- **Rate Limiting**: Protect against abuse and ensure fair usage

### 🔒 Security Best Practices

#### Authentication & Authorization:
```python
# JWT Token implementation
class AuthService:
    def generate_token(self, user: User) -> str:
        payload = {
            'user_id': user.id,
            'email': user.email,
            'roles': [role.name for role in user.roles],
            'exp': datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_token(self, token: str) -> Dict:
        try:
            return jwt.decode(token, self.secret_key, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token expired")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Invalid token")
```

#### Input Validation:
```python
# Pydantic models for validation
class CreateUserRequest(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=0, le=120)
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()
```

#### Data Protection:
- **Encryption at Rest**: Sensitive data encrypted in database
- **Encryption in Transit**: HTTPS/TLS for all communications
- **Secrets Management**: Environment variables or vault for secrets
- **Data Minimization**: Collect only necessary data
- **Regular Audits**: Log access to sensitive data

### 📊 Monitoring & Observability

#### Structured Logging:
```python
import structlog

logger = structlog.get_logger()

# Log with context
logger.info(
    "User login attempt",
    user_id=user.id,
    ip_address=request.remote_addr,
    user_agent=request.headers.get('User-Agent'),
    timestamp=datetime.utcnow().isoformat()
)
```

#### Health Checks:
```python
class HealthCheckService:
    def check_database(self) -> HealthStatus:
        try:
            self.db.execute("SELECT 1")
            return HealthStatus.HEALTHY
        except Exception as e:
            return HealthStatus.UNHEALTHY
    
    def check_external_service(self) -> HealthStatus:
        try:
            response = requests.get(self.external_url, timeout=5)
            return HealthStatus.HEALTHY if response.status_code == 200 else HealthStatus.DEGRADED
        except Exception:
            return HealthStatus.UNHEALTHY
```

#### Metrics Collection:
- **Business Metrics**: User registrations, conversion rates
- **Technical Metrics**: Response times, error rates, resource usage
- **Custom Metrics**: Feature usage, A/B test results
- **Alerting**: Proactive notification of issues

### 🧪 Testing Best Practices

#### Test Pyramid:
```
    /\
   /  \     E2E Tests (Few)
  /____\
 /      \   Integration Tests (Some)
/_______\  Unit Tests (Many)
```

#### Test Categories:
```python
# Unit Tests - Fast, isolated
def test_user_validation():
    user = User(email="test@example.com", name="Test User")
    assert user.is_valid()

# Integration Tests - Database, external services
def test_user_repository():
    user = User(email="test@example.com", name="Test User")
    saved_user = user_repository.save(user)
    assert saved_user.id is not None

# End-to-End Tests - Full user journey
def test_user_registration_flow(client):
    response = client.post("/register", json={
        "email": "test@example.com",
        "name": "Test User",
        "password": "securepassword"
    })
    assert response.status_code == 201
```

### 🔄 DevOps & Deployment

#### CI/CD Pipeline:
```yaml
# GitHub Actions example
name: CI/CD Pipeline
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: pytest --cov=src tests/
      
  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: ./deploy.sh
```

#### Infrastructure as Code:
```yaml
# Docker Compose for local development
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/myapp
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
  
  redis:
    image: redis:6-alpine
```

### 🌿 Nature's Way Development Practices

#### Abundance Mindset:
- **Knowledge Sharing**: Regular code reviews and pair programming
- **Documentation**: Living documentation that grows with the system
- **Open Source**: Contribute back to community when possible
- **Mentoring**: Share expertise without expectation of return

#### Sustainable Development:
- **Technical Debt Management**: Regular refactoring cycles
- **Team Wellness**: Sustainable pace, work-life balance
- **Continuous Learning**: Regular learning time for team growth
- **Collective Ownership**: Shared responsibility for code quality

#### Collaboration Practices:
- **Daily Standups**: Brief, focused team synchronization
- **Sprint Planning**: Collaborative effort estimation and planning
- **Retrospectives**: Regular team improvement discussions
- **Pair Programming**: Knowledge sharing and code quality improvement

### 📈 Scalability Considerations

#### Horizontal Scaling:
- **Stateless Services**: No server-side session storage
- **Load Balancing**: Distribute requests across multiple instances
- **Database Sharding**: Partition data across multiple databases
- **CDN Usage**: Global content distribution

#### Vertical Scaling:
- **Resource Optimization**: CPU and memory usage optimization
- **Connection Pooling**: Efficient database connection management
- **Caching Layers**: Reduce database load with strategic caching
- **Query Optimization**: Efficient database query patterns

## 🎯 Implementation Checklist

### Immediate (Week 1):
- [ ] Set up CI/CD pipeline
- [ ] Implement basic logging
- [ ] Add health check endpoints
- [ ] Configure environment-based settings

### Short-term (Month 1):
- [ ] Implement comprehensive testing
- [ ] Set up monitoring and alerting
- [ ] Add security headers and validation
- [ ] Document API endpoints

### Long-term (Quarter 1):
- [ ] Performance optimization
- [ ] Advanced monitoring dashboards
- [ ] Automated security scanning
- [ ] Disaster recovery procedures

*Best practices shared abundantly for collective development excellence and sustainable software craftsmanship.*
"""
