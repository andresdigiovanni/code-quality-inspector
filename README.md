# Code Quality Inspector

CodeMetricAnalyzer is a Python library that simplifies the analysis and assessment of code quality metrics in software development projects. With this library, you can measure cyclomatic complexity, cognitive complexity, maintainability, and other key metrics in your code.


# Metrics

## Cyclomatic Complexity

- **0 to 10**: Low cyclomatic complexity.
  - Simple and easy-to-understand code.
  - Linear and straightforward control flow.
  - Few independent logical paths.

- **11 to 20**: Moderate cyclomatic complexity.
  - Code is more complex but still manageable.
  - May include nested control structures.
  - Multiple independent logical paths but reasonably understandable.

- **21 to 50**: High cyclomatic complexity.
  - Code is fairly complex with intricate control structure.
  - Difficult to understand and maintain.
  - Many nested control structures and multiple independent logical paths.

- **Above 50**: Very high cyclomatic complexity.
  - Extremely complex and challenging to comprehend.
  - Highly error-prone and difficult to maintain.
  - Many independent logical paths and highly intricate control structure.

## Maintainability

- **0 to 20**: Very low maintainability.
  - Code is very difficult to maintain and understand.
  - Highly error-prone and challenging to work with.
  - Requires extensive review and refactoring.

- **21 to 40**: Low maintainability.
  - Code has poor maintainability and quality.
  - Can be challenging to understand and maintain.
  - May require some refactoring and improvements.

- **41 to 60**: Moderate maintainability.
  - Code has acceptable maintainability and quality.
  - Reasonably readable and modifiable.
  - Some minor improvements may be needed.

- **61 to 80**: High maintainability.
  - Code is of high quality in terms of maintainability.
  - Easy to understand and maintain.
  - Requires minimal additional maintenance effort.

- **81 to 100**: Very high maintainability.
  - Code is of the highest quality in terms of maintainability.
  - Highly readable and modifiable.
  - Requires minimal ongoing maintenance and is highly reliable.

# Example

```python

# Define directories
project_directory = "project_directory/"
output_directory = "quality_inspector_result/"

# Instance of CodeQualityInspector
cqi = CodeQualityInspector(project_directory)

# Analize project
cqi.inspect_project()

# Write csv results
cqi.write_metrics_to_csv(output_directory)

```
