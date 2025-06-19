"""ZV.0 - Single File AI Code Analysis Agent

A comprehensive code analysis tool in a single file for easy distribution.
"""

import ast
import yaml
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('zv0')

class CodeIssue:
    """Represents a code issue."""
    def __init__(self, severity: str, line_number: int, message: str, category: str = "general"):
        self.severity = severity
        self.line_number = line_number
        self.message = message
        self.category = category

class ComplexityMetrics:
    """Contains code complexity metrics."""
    def __init__(self, cyclomatic_complexity: int, lines_of_code: int, 
                 comment_ratio: float, function_count: int, class_count: int):
        self.cyclomatic_complexity = cyclomatic_complexity
        self.lines_of_code = lines_of_code
        self.comment_ratio = comment_ratio
        self.function_count = function_count
        self.class_count = class_count

class AnalysisReport:
    """Contains analysis results."""
    def __init__(self, overall_score: int, security_score: int, 
                 maintainability_score: int, performance_score: int,
                 complexity_metrics: ComplexityMetrics, issues: List[CodeIssue],
                 suggestions: List[str]):
        self.overall_score = overall_score
        self.security_score = security_score
        self.maintainability_score = maintainability_score
        self.performance_score = performance_score
        self.complexity_metrics = complexity_metrics
        self.issues = issues
        self.suggestions = suggestions

class ZV0Agent:
    """Main ZV.0 Agent class."""
    
    def __init__(self, config_path: str = None):
        """Initialize the agent."""
        self.config = self._load_config(config_path)
        self.analyzer = CodeAnalyzer()
        logger.info("ZV0Agent initialized")
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration."""
        if not config_path:
            return self._default_config()
            
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.warning(f"Error loading config: {str(e)}")
            return self._default_config()
            
    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            "agent": {
                "name": "ZV.0",
                "version": "1.0.0"
            },
            "analysis": {
                "security_checks": True,
                "performance_checks": True
            }
        }
        
    def analyze_file(self, file_path: str, language: str = "python") -> Dict[str, Any]:
        """Analyze a single file."""
        try:
            with open(file_path, 'r') as f:
                code = f.read()
                
            report = self.analyzer.analyze_code(code, language, file_path)
            
            return {
                "success": True,
                "data": {
                    "overall_score": report.overall_score,
                    "issues": len(report.issues),
                    "suggestions": report.suggestions
                }
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

class CodeAnalyzer:
    """Core code analysis engine."""
    
    def analyze_code(self, code: str, language: str, file_path: str) -> AnalysisReport:
        """Analyze code string."""
        try:
            tree = ast.parse(code)
            metrics = self._calculate_metrics(tree, code)
            issues = self._analyze_code(tree)
            scores = self._calculate_scores(issues, metrics)
            
            return AnalysisReport(
                overall_score=scores['overall'],
                security_score=scores['security'],
                maintainability_score=scores['maintainability'],
                performance_score=scores['performance'],
                complexity_metrics=metrics,
                issues=issues,
                suggestions=self._generate_suggestions(issues)
            )
        except Exception as e:
            logger.error(f"Analysis error: {str(e)}")
            return self._error_report(str(e))
            
    def _calculate_metrics(self, tree: ast.AST, code: str) -> ComplexityMetrics:
        """Calculate code metrics."""
        lines = code.split('\n')
        loc = len([line for line in lines if line.strip()])
        comment_lines = len([line for line in lines if line.strip().startswith('#')])
        
        complexity = 1
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.And, ast.Or)):
                complexity += 1
                
        function_count = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
        class_count = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])
        
        return ComplexityMetrics(
            cyclomatic_complexity=complexity,
            lines_of_code=loc,
            comment_ratio=comment_lines / loc if loc > 0 else 0,
            function_count=function_count,
            class_count=class_count
        )
        
    def _analyze_code(self, tree: ast.AST) -> List[CodeIssue]:
        """Perform code analysis."""
        issues = []
        
        # Security checks
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                    if func_name in ['eval', 'exec', 'open']:
                        issues.append(CodeIssue(
                            severity="high",
                            line_number=node.lineno,
                            message=f"Potentially dangerous function: {func_name}",
                            category="security"
                        ))
        
        # Complexity checks
        loop_depth = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                loop_depth += 1
                if loop_depth > 2:
                    issues.append(CodeIssue(
                        severity="medium",
                        line_number=node.lineno,
                        message=f"Deeply nested loops (depth {loop_depth})",
                        category="performance"
                    ))
            elif isinstance(node, ast.FunctionDef):
                loop_depth = 0
                
        return issues
        
    def _calculate_scores(self, issues: List[CodeIssue], metrics: ComplexityMetrics) -> Dict[str, int]:
        """Calculate quality scores."""
        scores = {
            'overall': 100,
            'security': 100,
            'maintainability': 100,
            'performance': 100
        }
        
        for issue in issues:
            if issue.severity == "high":
                deduction = 5
            elif issue.severity == "medium":
                deduction = 3
            else:
                deduction = 1
                
            if issue.category == "security":
                scores['security'] -= deduction
            elif issue.category == "performance":
                scores['performance'] -= deduction
                
            scores['overall'] -= deduction
            
        if metrics.cyclomatic_complexity > 10:
            scores['maintainability'] -= 10
            scores['overall'] -= 5
            
        for key in scores:
            scores[key] = max(0, scores[key])
            
        return scores
        
    def _generate_suggestions(self, issues: List[CodeIssue]) -> List[str]:
        """Generate improvement suggestions."""
        return [f"{issue.category.capitalize()}: {issue.message}" for issue in issues]
        
    def _error_report(self, error: str) -> AnalysisReport:
        """Create error report."""
        return AnalysisReport(
            overall_score=0,
            security_score=0,
            maintainability_score=0,
            performance_score=0,
            complexity_metrics=ComplexityMetrics(0, 0, 0, 0, 0),
            issues=[CodeIssue("high", 0, f"Analysis error: {error}")],
            suggestions=["Check your input code"]
        )

# Example Usage
if __name__ == "__main__":
    agent = ZV0Agent()
    
    # Analyze a sample code
    sample_code = """
def example():
    x = 1
    return x
"""
    
    report = agent.analyzer.analyze_code(sample_code, "python", "example.py")
    print(f"Analysis Report:")
    print(f"Overall Score: {report.overall_score}")
    print(f"Issues Found: {len(report.issues)}")
    print("Suggestions:")
    for suggestion in report.suggestions:
        print(f"- {suggestion}")