from dataclasses import dataclass
from typing import List, Optional
import yaml

@dataclass
class Rule:
    id: str
    name: str
    when: str
    assert_expr: str
    severity: str = "warn"
    explain: Optional[str] = None

def load_rules(path) -> List[Rule]:
    data = yaml.safe_load(open(path, "r", encoding="utf-8"))
    rules: List[Rule] = []
    for item in data or []:
        rules.append(
            Rule(
                id=item["id"],
                name=item["name"],
                when=item["when"],
                assert_expr=item["assert"],
                severity=item.get("severity", "warn"),
                explain=item.get("explain")
            )
        )
    return rules