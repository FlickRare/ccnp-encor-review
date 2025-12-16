# PyATS Direct Connectivity Test - Refactoring Guide

## Current Issues

### 1. **Code Organization**
- All logic in a single script with no functions
- Testbed loading, SSH configuration, and testing logic all mixed together
- Difficult to test, reuse, or extend

### 2. **Error Handling**
- Generic `except Exception` catches too much
- No proper logging framework (using print statements)
- Silent failures don't provide actionable feedback

### 3. **Hard-coded Values**
- SSH options hard-coded in the script
- Success threshold (>50%) is magic number
- Prefix filter (/30) is hard-coded

### 4. **Variable Naming**
- `subj_interfacess` - unused variable with typo
- `split_ipv4_add` - unclear naming
- `intf_ipv4_data` - inconsistent abbreviations

### 5. **Missing Features**
- No CLI arguments (testbed path, filters, thresholds)
- No structured output (JSON/CSV for automation)
- No summary report at the end

## Refactoring Steps

### Step 1: Extract Functions

**Create these functions:**
```python
def load_testbed_with_ssh_options(testbed_path, disable_strict_host_checking=True)
def connect_device(device, timeout=30)
def get_p2p_interfaces(device, prefix_length=30)
def test_interface_connectivity(device, interface, neighbor_ip, threshold=80)
def run_connectivity_tests(testbed_path, prefix_filter=30, success_threshold=80)
```

### Step 2: Add Proper Logging

Replace all `print()` statements with Python's `logging` module:
```python
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
```

### Step 3: Add CLI Arguments

Use `argparse` to make the script configurable:
```python
parser = argparse.ArgumentParser(description='Test P2P connectivity')
parser.add_argument('--testbed', default='testbed.yaml')
parser.add_argument('--prefix-length', type=int, default=30)
parser.add_argument('--threshold', type=int, default=80)
parser.add_argument('--output', choices=['text', 'json', 'csv'])
```

### Step 4: Improve Error Handling

- Create custom exception classes for specific failures
- Use specific exception types (ConnectionError, ValueError)
- Implement retry logic for transient failures
- Log full tracebacks for debugging

### Step 5: Add Data Classes

Use dataclasses for structured results:
```python
@dataclass
class ConnectivityTest:
    device: str
    interface: str
    neighbor_ip: str
    success_rate: float
    passed: bool
```

### Step 6: Create Summary Report

Track all test results and generate a summary:
- Total tests run
- Pass/fail counts
- Failed connections list
- Execution time

### Step 7: Add Type Hints

Add type annotations to all functions for better IDE support and documentation.

## Recommended Structure

```
pyats/
├── direct_connect_test.py      # Main entry point (minimal)
├── connectivity_tester/
│   ├── __init__.py
│   ├── testbed.py              # Testbed loading/configuration
│   ├── device.py               # Device connection logic
│   ├── tests.py                # Connectivity test logic
│   ├── reporting.py            # Results and reports
│   └── exceptions.py           # Custom exceptions
└── tests/
    └── test_connectivity.py    # Unit tests
```

## Priority Order

1. **High Priority**: Extract functions, add logging (improves maintainability immediately)
2. **Medium Priority**: CLI arguments, better error handling (makes tool more flexible)
3. **Low Priority**: Data classes, type hints, restructuring (nice-to-have improvements)

## Quick Wins

Start with these small changes:
1. Fix the typo: `subj_interfacess` → remove (unused)
2. Extract SSH options to a constant at the top
3. Extract magic numbers (50, 30) to named constants
4. Rename variables: `split_ipv4_add` → `ipv4_config`, `intf_ipv4_data` → `interface_ipv4`
5. Move `import yaml` to the top with other imports

## Testing Strategy

Before refactoring:
1. Run the script and save output as baseline
2. After each refactor step, run again and compare output
3. Ensure functionality remains identical during restructuring
