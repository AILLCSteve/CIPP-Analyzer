# Claude Code Project Instructions

## Core Development Philosophy

### Project Initialization Protocol
Before writing any code, you MUST:

1. **Brainstorm Multiple Approaches**: Consider at least 3 different implementation strategies:
   - Desktop application (Electron, Tauri, native)
   - Web application (various frameworks)
   - CLI tool
   - Library/Package
   - Script-based solution
   - Hybrid approach

2. **Document the Chosen Approach**: Explain WHY the selected approach best fits the requirements, considering:
   - User needs and technical proficiency
   - Deployment requirements
   - Performance considerations
   - Maintenance complexity
   - Scalability needs

3. **Architecture Planning**: Create an architecture document outlining:
   - Core components and their responsibilities
   - Data flow between components
   - External dependencies and their purpose
   - Potential scaling points and bottlenecks

## Configuration Management

### Environment Configuration
- **NEVER hardcode configuration values** (ports, API endpoints, database connections)
- Create a centralized configuration system using environment variables
- Implement a config hierarchy: defaults → environment → runtime overrides

#### Required Configuration Structure
```
/config
  ├── default.json     # Default configuration values
  ├── development.json # Development overrides
  ├── production.json  # Production settings
  └── config.js       # Configuration loader with validation
```

#### Port Management for Web Applications
- Use a single PORT environment variable that cascades to all services
- Implement automatic port detection and fallback:
  ```javascript
  const PORT = process.env.PORT || findAvailablePort(3000, 3100);
  ```
- Create a cleanup script that kills processes on all potential ports before starting
- Log the actual port being used prominently on startup

### Process Management
- Implement proper shutdown handlers for all services
- Create a `cleanup.sh` script that kills orphaned processes
- Use process managers (PM2, nodemon) with proper configuration
- Implement health checks and automatic restart on failure

## Git Workflow & Version Control

### Branch Management
Before making ANY code changes:
1. **Create a new feature branch**: `git checkout -b feature/[descriptive-name]`
2. **Never commit directly to main/master**
3. **Use semantic commit messages**: 
   - `feat:` for new features
   - `fix:` for bug fixes
   - `refactor:` for code improvements
   - `test:` for test additions/modifications
   - `docs:` for documentation updates

### Pre-commit Checks
Implement git hooks that enforce:
- Code formatting (Prettier/Black/rustfmt)
- Linting (ESLint/Pylint/Clippy)
- Unit test execution
- Build verification

## SOLID Design Principles

### Single Responsibility Principle (SRP)
- Each module/class should have ONE reason to change
- Functions should do ONE thing well
- If you need "and" to describe what a function does, split it

### Open/Closed Principle (OCP)
- Design modules to be open for extension but closed for modification
- Use interfaces/protocols for extensibility
- Implement plugin architectures where appropriate

### Liskov Substitution Principle (LSP)
- Derived classes must be substitutable for their base classes
- Avoid breaking changes in inherited behaviors
- Test polymorphic code paths thoroughly

### Interface Segregation Principle (ISP)
- Create focused, specific interfaces rather than large, general ones
- Clients should not depend on methods they don't use
- Prefer multiple small interfaces over one large interface

### Dependency Inversion Principle (DIP)
- Depend on abstractions, not concretions
- High-level modules should not depend on low-level modules
- Use dependency injection for flexibility

## Testing Strategy

### Comprehensive Testing Approach

#### 1. Unit Tests
- Minimum 80% code coverage
- Test edge cases and error conditions
- Mock external dependencies
- Each module should have a corresponding test file

#### 2. Integration Tests
- Test component interactions
- Verify data flow between modules
- Test with real (test) databases and services
- Cover critical user paths

#### 3. End-to-End (E2E) Tests
**CRITICAL**: These tests MUST simulate actual user behavior:
- Use tools like Playwright, Cypress, or Selenium
- Test the ACTUAL compiled/built application, not just components
- Include tests for:
  - Application startup and initialization
  - All user-facing features
  - Error states and recovery
  - Performance under load
  - Browser compatibility (for web apps)
  - OS compatibility (for desktop apps)

#### 4. User Acceptance Testing (UAT) Checklist
Create a manual testing checklist that includes:
- [ ] Application starts without errors
- [ ] All UI elements are visible and responsive
- [ ] Features work as expected from a user perspective
- [ ] Error messages are helpful and actionable
- [ ] Performance is acceptable
- [ ] Data persists correctly
- [ ] Application handles network interruptions gracefully

### Testing Implementation Requirements
```
/tests
  ├── unit/           # Unit tests for individual modules
  ├── integration/    # Integration tests
  ├── e2e/           # End-to-end tests
  ├── fixtures/      # Test data and mocks
  └── coverage/      # Coverage reports
```

## Modular Architecture & Documentation

### Module Organization
Each module/feature MUST include:

```
/src/modules/[module-name]/
  ├── index.js           # Module entry point
  ├── README.md          # Module documentation
  ├── tests/            # Module-specific tests
  ├── dependencies.json # Explicit dependencies
  └── INTERACTIONS.md   # How this module affects others
```

### Module Documentation Template (README.md)
```markdown
# Module: [Module Name]

## Purpose
Brief description of what this module does and why it exists.

## Public API
List of exported functions/classes with their signatures.

## Dependencies
- Internal: List of other modules this depends on
- External: NPM packages or external services

## Side Effects
Any global state changes, file I/O, network calls, etc.

## Affected By
List of modules that can affect this module's behavior.

## Affects
List of modules that this module can affect.

## Configuration
Required environment variables or configuration options.

## Error Handling
Common errors and how they're handled.

## Performance Considerations
Any performance implications or optimization notes.

## Testing
How to test this module in isolation.
```

### Module Registry
Maintain a central `MODULE_REGISTRY.md` file at the project root:
```markdown
# Module Registry

## Core Modules
| Module | Purpose | Dependencies | Affects | Last Modified |
|--------|---------|--------------|---------|---------------|
| auth   | User authentication | db, crypto | All API routes | 2024-01-15 |
| database | Data persistence | none | auth, api | 2024-01-14 |

## Feature Modules
[Similar table structure]

## Utility Modules
[Similar table structure]
```

## Code Quality Standards

### Code Style
- Use consistent formatting (enforce with tools)
- Maximum function length: 50 lines
- Maximum file length: 300 lines
- Clear, descriptive variable names
- Comprehensive inline documentation for complex logic

### Error Handling
- Never silently swallow errors
- Implement proper error boundaries
- Log errors with context
- Provide actionable error messages to users
- Implement retry logic for transient failures

### Performance
- Profile before optimizing
- Implement lazy loading where appropriate
- Use caching strategically
- Monitor memory usage
- Implement request debouncing/throttling

## Development Workflow

### Daily Development Cycle
1. Review MODULE_REGISTRY.md before starting
2. Create feature branch
3. Update affected module documentation
4. Write tests first (TDD when possible)
5. Implement feature
6. Run full test suite
7. Update MODULE_REGISTRY.md if dependencies changed
8. Commit with semantic message
9. Create pull request with checklist

### Pre-Release Checklist
- [ ] All tests passing
- [ ] E2E tests cover new features
- [ ] Performance benchmarks acceptable
- [ ] Security scan completed
- [ ] Documentation updated
- [ ] MODULE_REGISTRY.md current
- [ ] Configuration for all environments verified
- [ ] Rollback plan documented

## Project-Specific Instructions

### CIPP Analyzer Specific Requirements

#### Security Configuration Management
**CRITICAL: API Key Protection**

This project uses OpenAI API keys that must NEVER be committed to version control.

**Configuration Setup:**
1. **config.json** - Local configuration file (NEVER commit this)
   - Contains sensitive API keys and configuration
   - Located in project root
   - Automatically excluded via .gitignore

2. **Configuration Loading Priority:**
   - Primary: `config.json` (local file, gitignored)
   - Fallback: localStorage (browser storage)
   - Default: Empty values in code

**Git Workflow for This Project:**
```bash
# .gitignore ALWAYS excludes:
# - config.json (contains API keys)
# - Any other sensitive configuration files

# When committing changes:
git add .                    # This will automatically skip config.json
git status                   # Verify config.json is NOT staged
git commit -m "your message"
git push
```

**Setting Up on New Machine:**
1. Clone the repository
2. Create your own `config.json` file with your API keys:
   ```json
   {
     "apiKey": "your-openai-api-key-here",
     "gptModel": "gpt-4",
     "defaultChunkSize": 1500,
     "analysisTimeout": 60,
     "autoRetry": true,
     "rateLimitDelay": 2000,
     "maxTokensPerRequest": 8000
   }
   ```
3. config.json will be automatically ignored by git

**IMPORTANT REMINDERS:**
- ⚠️ **NEVER** remove config.json from .gitignore
- ⚠️ **NEVER** hardcode API keys in source files
- ⚠️ **ALWAYS** verify `git status` before pushing to ensure config.json is not staged
- ⚠️ If you accidentally commit an API key, immediately revoke it and generate a new one

### Custom Configuration

**Technology Stack:**
- Frontend: HTML5 + Vanilla JavaScript
- API: OpenAI GPT-4
- Storage: Browser localStorage + local config.json file
- PDF Processing: Python (pdf_extractor.py)

### Special Considerations

1. **Browser-based Application**: This is a client-side web application that runs in the browser
2. **CORS Considerations**: config.json must be served from same origin
3. **API Key Security**: Keys are loaded client-side; consider backend proxy for production
4. **Python Dependencies**: pdf_extractor.py requires Python 3.x and dependencies from requirements.txt

---

## Appendix A: Common Pitfalls to Avoid

1. **Hardcoded Values**: Always use configuration
2. **Tight Coupling**: Use dependency injection
3. **Missing Error Handling**: Every async operation needs try/catch
4. **Incomplete Tests**: E2E tests must test actual user experience
5. **Poor Documentation**: Every module needs complete documentation
6. **Resource Leaks**: Always cleanup (event listeners, timers, connections)
7. **Security Oversights**: Never trust user input, always sanitize
8. **Performance Assumptions**: Measure, don't guess

## Appendix B: Quick Commands

```bash
# Development
npm run dev          # Start development server
npm run test         # Run all tests
npm run test:e2e     # Run E2E tests only
npm run lint         # Check code style
npm run cleanup      # Kill all processes and clean ports

# Git
git checkout -b feature/new-feature  # Create feature branch
git hooks install                    # Install git hooks

# Documentation
npm run docs:generate  # Generate documentation
npm run docs:serve     # Serve documentation locally
```

## Appendix C: Emergency Procedures

### When Things Go Wrong
1. Check MODULE_REGISTRY.md for affected modules
2. Review recent commits: `git log --oneline -10`
3. Run cleanup script: `./scripts/cleanup.sh`
4. Check error logs: `tail -f logs/error.log`
5. Rollback if necessary: `git revert HEAD`
6. Run full test suite to verify fix

---

*This document is a living guide. Update it as the project evolves.*
*Last Updated: [Date]*
*Version: 1.0.0*