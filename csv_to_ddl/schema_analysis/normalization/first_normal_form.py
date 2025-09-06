import logging
from typing import List

from schema_analysis.models.table import NormalizationSuggestion, TableSpec
from schema_analysis.normalization.base_normal_form import NormalForm


class FirstNormalForm(NormalForm):

    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)

    def check(self, table_name: str, header: List[str],
              rows: List[List[str]], table_spec: TableSpec) -> List[NormalizationSuggestion]:
        """
        First Normal Form violation detection algorithm.
        
        Detects multi-valued attributes that violate 1NF atomicity requirement.
        1NF requires that each cell contains only a single, atomic value.
        
        Process:
        1. For each column, scan all cell values for multi-value indicators:
           - Common separators: comma (,), semicolon (;), pipe (|)
           - Whitespace separators: newline (\n), tab (\t)
        2. Calculate violation ratio: cells with separators / total cells
        3. Generate suggestions for columns above threshold (10%)
        
        Multi-value violations typically occur in:
        - Tag/category lists: "red, blue, green"
        - Contact info: "email1; email2; email3"
        - Addresses with embedded newlines
        
        Solutions suggest:
        - Separate columns for each value
        - Junction tables for many-to-many relationships
        
        Returns:
            List of normalization suggestions for 1NF violations
        """
        suggestions = []

        if not rows or not header:
            return suggestions

        for col_idx, col_name in enumerate(header):
            # Multi-value pattern indicators
            multi_value_indicators = [',', ';', '|', '\n', '\t']
            multi_value_count = 0
            total_count = 0

            # Scan column for multi-value patterns
            for row in rows:
                if col_idx < len(row) and row[col_idx]:
                    cell_value = str(row[col_idx]).strip()
                    total_count += 1

                    # Check for any multi-value separator
                    for indicator in multi_value_indicators:
                        if indicator in cell_value:
                            multi_value_count += 1
                            break  # Count cell once even if multiple separators

            # Generate suggestion if violation ratio exceeds threshold
            if total_count > 0:
                multi_value_ratio = multi_value_count / total_count

                if multi_value_ratio >= 0.1:  # 10% threshold for significance
                    description = (
                        f"Column '{col_name}' contains multi-valued data in {multi_value_ratio:.1%} of rows. "
                        f"Consider splitting into separate columns or creating a separate '{col_name}_values' table.")

                    suggestion = NormalizationSuggestion(
                        table_name=table_name,
                        suggestion_type="1NF",
                        description=description,
                        confidence=multi_value_ratio
                    )
                    suggestions.append(suggestion)

        return suggestions
