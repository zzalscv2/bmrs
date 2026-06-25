# Code Smell Taxonomy

## Overview

A **code smell** is a surface indication in source code that suggests a deeper design, implementation, or maintainability problem. Code smells are not necessarily bugs; rather, they increase technical debt by making software more difficult to understand, modify, test, and evolve.

---

# Code Smell Taxonomy

| Category | Code Smell | Definition | Typical Consequences |
|-----------|------------|------------|----------------------|
| **Size** | Long Method | A method that has grown too large and performs multiple responsibilities. | Poor readability, difficult testing, low cohesion. |
| | Large Class | A class containing excessive data, methods, or responsibilities. | Reduced cohesion, difficult maintenance. |
| | God Class (Blob) | A class that centralises most of the system's behaviour and data. | Tight coupling, poor modularity, difficult evolution. |
| | Long Parameter List | A function requiring many parameters to operate. | Poor abstraction, difficult use, increased errors. |
| | Data Clumps | Groups of variables that repeatedly appear together. | Duplicate knowledge and missing abstractions. |
| **Complexity** | Complex Conditional | Large or deeply nested conditional logic. | Difficult understanding and testing. |
| | Deep Nesting | Multiple nested loops or conditional statements. | Reduced readability and increased cognitive load. |
| | Excessive Cyclomatic Complexity | Too many independent execution paths through a function. | Poor testability and increased defect risk. |
| | Switch Statements | Large switch/case structures controlling behaviour. | Violates Open-Closed Principle and hinders extensibility. |
| **Duplication** | Duplicate Code | Identical or nearly identical code appears in multiple places. | Inconsistent fixes and increased maintenance effort. |
| | Repeated Knowledge | Business rules or algorithms implemented multiple times, even if written differently. | Inconsistent behaviour and technical debt. |
| | Copy-and-Paste Programming | Code duplicated by copying rather than abstraction. | Error propagation and maintenance burden. |
| **Abstraction** | Primitive Obsession | Primitive types used instead of meaningful domain objects. | Weak domain modelling and poor readability. |
| | Speculative Generality | Abstractions created for anticipated future requirements that never occur. | Unnecessary complexity. |
| | Lazy Class | A class providing too little functionality to justify its existence. | Needless indirection. |
| | Refused Bequest | A subclass inherits behaviour it does not need or actively ignores. | Incorrect inheritance hierarchy. |
| | Temporary Field | Instance variables are only required under limited circumstances. | Confusing object state. |
| **Encapsulation** | Feature Envy | A method relies more on another object's data than its own. | High coupling and misplaced responsibilities. |
| | Message Chains | Long chains of method calls to access distant objects. | Fragile coupling and Law of Demeter violations. |
| | Middle Man | A class delegates nearly all work to another class. | Unnecessary indirection. |
| | Inappropriate Intimacy | Classes depend excessively on each other's implementation details. | Tight coupling and reduced modularity. |
| **Data** | Data Class | A class that only stores data with little or no behaviour. | Weak encapsulation and anemic domain model. |
| | Global Mutable State | Shared mutable variables accessible throughout the program. | Hidden dependencies and unpredictable behaviour. |
| | Magic Values | Numeric or string literals appear without explanation. | Poor readability and maintainability. |
| **Dependencies** | Circular Dependency | Components depend directly or indirectly on each other. | Prevents modular development and reuse. |
| | Hidden Dependency | Dependencies are created internally rather than explicitly supplied. | Difficult testing and maintenance. |
| | Hard-coded Dependency | Specific implementations are instantiated directly. | Violates Dependency Inversion Principle. |
| **Maintainability** | Divergent Change | A class changes for many unrelated reasons. | Violates Single Responsibility Principle. |
| | Shotgun Surgery | One logical change requires modifications in many files. | High maintenance effort. |
| | Dead Code | Code that is never executed or no longer contributes functionality. | Increased maintenance cost and confusion. |
| | Misleading Comment | Documentation contradicts or obscures the implementation. | Incorrect understanding by developers. |
| | Poor Naming | Variables, methods, or classes fail to communicate intent. | Reduced readability and analysability. |
| **Configuration** | Hard-coded Setting | Configuration values embedded directly within source code. | Reduced portability and flexibility. |
| | Hard-coded File Path | Absolute or fixed file paths within source code. | Environment-specific failures. |
| | Embedded Credentials | Passwords, API keys, or secrets stored directly in code. | Security vulnerabilities. |
| **Testing** | Hidden Side Effects | A function performs unexpected modifications beyond its stated purpose. | Difficult unit testing and debugging. |
| | Non-deterministic Behaviour | Code produces different outputs under identical inputs. | Unreliable automated testing. |
| | Static Dependencies | Static/global resources prevent isolated testing. | Poor testability. |
| **Resources** | Resource Leak | Files, sockets, or database connections are not properly released. | Memory leaks and resource exhaustion. |
| | Improper Exception Cleanup | Exceptions bypass resource cleanup. | Resource leaks and inconsistent state. |
| **Architecture** | God Component | A subsystem accumulates excessive architectural responsibility. | Architectural erosion. |
| | Layer Violation | Components bypass intended architectural layers. | Increased coupling and reduced maintainability. |
| | Cyclic Architecture | Architectural modules depend upon each other. | Poor modularity and difficult deployment. |
| | Hub-like Dependency | One module becomes the central dependency for many others. | Single point of maintenance failure. |

---

# Taxonomy by Category

```
Code Smells
│
├── Size
│   ├── Long Method
│   ├── Large Class
│   ├── God Class
│   ├── Long Parameter List
│   └── Data Clumps
│
├── Complexity
│   ├── Complex Conditional
│   ├── Deep Nesting
│   ├── Switch Statements
│   └── Excessive Cyclomatic Complexity
│
├── Duplication
│   ├── Duplicate Code
│   ├── Repeated Knowledge
│   └── Copy-and-Paste Programming
│
├── Abstraction
│   ├── Primitive Obsession
│   ├── Lazy Class
│   ├── Temporary Field
│   ├── Refused Bequest
│   └── Speculative Generality
│
├── Encapsulation
│   ├── Feature Envy
│   ├── Message Chains
│   ├── Middle Man
│   └── Inappropriate Intimacy
│
├── Data
│   ├── Data Class
│   ├── Global Mutable State
│   └── Magic Values
│
├── Dependencies
│   ├── Hidden Dependency
│   ├── Hard-coded Dependency
│   └── Circular Dependency
│
├── Maintainability
│   ├── Divergent Change
│   ├── Shotgun Surgery
│   ├── Dead Code
│   ├── Misleading Comment
│   └── Poor Naming
│
├── Configuration
│   ├── Hard-coded Setting
│   ├── Hard-coded File Path
│   └── Embedded Credentials
│
├── Testing
│   ├── Hidden Side Effects
│   ├── Static Dependencies
│   └── Non-deterministic Behaviour
│
├── Resources
│   ├── Resource Leak
│   └── Improper Exception Cleanup
│
└── Architecture
    ├── God Component
    ├── Layer Violation
    ├── Cyclic Architecture
    └── Hub-like Dependency
```

---

# Notes

- A single code fragment may exhibit multiple code smells simultaneously.
- Code smells are indicators of maintainability problems rather than functional defects.
- Multiple smells often arise from the same underlying design issue (for example, a God Class frequently contains Long Methods, Feature Envy, Duplicate Code, and Hidden Dependencies).
- Code smell detection should always be accompanied by developer judgement; not every smell necessarily warrants immediate refactoring.
- This taxonomy aligns well with maintainability characteristics defined in **ISO/IEC 25010**, particularly **Modularity**, **Analysability**, **Modifiability**, **Reusability**, and **Testability**.