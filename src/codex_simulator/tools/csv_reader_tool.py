import csv
import os
from typing import List, Dict, Any, Union, Optional
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

class CSVReaderToolInput(BaseModel):
    """Input schema for CSV Reader Tool."""
    file_path: str = Field(..., description="Path to the CSV file to read")
    delimiter: str = Field(",", description="Character used to separate fields (default: comma)")
    quotechar: str = Field('"', description="Character used to quote fields containing special characters")
    encoding: str = Field("utf-8", description="Character encoding of the CSV file")
    has_header: bool = Field(True, description="True if the first row is a header")
    output_format: str = Field("dict", description="Output format: 'list' for list of lists, 'dict' for list of dictionaries")
    max_rows: int = Field(0, description="Maximum number of rows to read (0 for all rows)")

class CSVReaderTool(BaseTool):
    """Tool for reading and parsing CSV files with Nature's Way abundance principles."""
    name: str = "csv_reader_tool"
    description: str = "Reads CSV files and extracts data in various formats, sharing insights abundantly for collective benefit"
    args_schema: type[BaseModel] = CSVReaderToolInput

    def __init__(self):
        super().__init__()
        # Initialize header as a private attribute to avoid Pydantic validation
        self._header: Optional[List[str]] = None
        self._last_file_info: Dict = {}

    @property
    def header(self) -> Optional[List[str]]:
        """Get the header from the last read CSV file."""
        return self._header

    def _run(self, file_path: str, delimiter: str = ",", quotechar: str = '"', 
             encoding: str = "utf-8", has_header: bool = True, 
             output_format: str = "dict", max_rows: int = 0) -> str:
        """
        Execute CSV reading with Nature's Way principles.
        
        Args:
            file_path: Path to the CSV file
            delimiter: Field separator character
            quotechar: Quote character for special fields
            encoding: File encoding
            has_header: Whether first row contains headers
            output_format: 'list' or 'dict' format
            max_rows: Maximum rows to read (0 = all)
        """
        try:
            # Validate file existence and accessibility
            validation_result = self._validate_file(file_path)
            if validation_result != "valid":
                return validation_result

            # Read the CSV file
            if output_format.lower() == "dict" and has_header:
                data, summary = self._read_csv_as_dicts(file_path, delimiter, quotechar, encoding, max_rows)
            else:
                data, summary = self._read_csv_as_lists(file_path, delimiter, quotechar, encoding, has_header, max_rows)

            if data is None:
                return "Error: Failed to read CSV file. Check file format and encoding."

            # Generate abundant response following Nature's Way
            return self._create_abundant_response(file_path, data, summary, output_format)

        except Exception as e:
            return f"CSV reading error: {str(e)}"

    def _validate_file(self, file_path: str) -> str:
        """Validate file existence and accessibility."""
        if not os.path.exists(file_path):
            return f"Error: File not found at '{file_path}'"
        
        if not os.path.isfile(file_path):
            return f"Error: Path '{file_path}' is not a file"
        
        if not os.access(file_path, os.R_OK):
            return f"Error: No read permission for file '{file_path}'"
        
        return "valid"

    def _read_csv_as_lists(self, file_path: str, delimiter: str, quotechar: str, 
                          encoding: str, has_header: bool, max_rows: int) -> tuple[Optional[List], Dict]:
        """Read CSV file as list of lists."""
        data = []
        summary = {"rows_read": 0, "columns": 0, "has_header": has_header}
        
        try:
            with open(file_path, 'r', newline='', encoding=encoding) as csvfile:
                reader = csv.reader(csvfile, delimiter=delimiter, quotechar=quotechar)
                
                # Handle header if present
                if has_header:
                    try:
                        self._header = next(reader)
                        summary["columns"] = len(self._header)
                    except StopIteration:
                        self._header = []
                        return [], {"error": "Empty file or header-only file"}
                
                # Read data rows
                for i, row in enumerate(reader):
                    if max_rows > 0 and i >= max_rows:
                        break
                    data.append(row)
                    summary["rows_read"] += 1
                
                if not has_header and data:
                    summary["columns"] = len(data[0]) if data[0] else 0
                
        except UnicodeDecodeError:
            return None, {"error": f"Encoding error with '{encoding}'. Try different encoding."}
        except csv.Error as e:
            return None, {"error": f"CSV parsing error: {e}"}
        except Exception as e:
            return None, {"error": f"Unexpected error: {e}"}
        
        return data, summary

    def _read_csv_as_dicts(self, file_path: str, delimiter: str, quotechar: str, 
                          encoding: str, max_rows: int) -> tuple[Optional[List], Dict]:
        """Read CSV file as list of dictionaries."""
        data = []
        summary = {"rows_read": 0, "columns": 0, "has_header": True}
        
        try:
            with open(file_path, 'r', newline='', encoding=encoding) as csvfile:
                reader = csv.DictReader(csvfile, delimiter=delimiter, quotechar=quotechar)
                self._header = reader.fieldnames
                
                if not self._header:
                    return [], {"error": "No header found or empty file"}
                
                summary["columns"] = len(self._header)
                
                for i, row in enumerate(reader):
                    if max_rows > 0 and i >= max_rows:
                        break
                    data.append(dict(row))
                    summary["rows_read"] += 1
                    
        except UnicodeDecodeError:
            return None, {"error": f"Encoding error. Try different encoding."}
        except csv.Error as e:
            return None, {"error": f"CSV parsing error: {e}"}
        except Exception as e:
            return None, {"error": f"Unexpected error: {e}"}
        
        return data, summary

    def _create_abundant_response(self, file_path: str, data: List, summary: Dict, output_format: str) -> str:
        """Create response following Nature's Way principles of abundant sharing."""
        # Store file info for potential reuse (abundance creation)
        self._last_file_info = {
            "file_path": file_path,
            "summary": summary,
            "header": self._header,
            "data_preview": data[:3] if len(data) > 3 else data
        }
        
        response = f"""
# CSV File Analysis - Abundant Data Extraction
*File: {file_path}*

## 📊 Data Summary
- **Rows processed**: {summary.get('rows_read', 0)}
- **Columns**: {summary.get('columns', 0)}
- **Header present**: {'Yes' if summary.get('has_header', False) else 'No'}
- **Output format**: {output_format}

## 📋 Structure Overview
"""
        
        # Add header information if available
        if self._header:
            response += f"""
### Column Headers:
{', '.join(f'"{col}"' for col in self._header)}
"""
        
        # Add data preview (first few rows)
        response += f"""
## 🔍 Data Preview (First {min(3, len(data))} rows):
"""
        
        if output_format.lower() == "dict" and data:
            for i, row in enumerate(data[:3]):
                response += f"\n**Row {i+1}:**\n"
                for key, value in row.items():
                    response += f"  - {key}: {value}\n"
        elif data:
            for i, row in enumerate(data[:3]):
                response += f"\n**Row {i+1}:** {', '.join(str(cell) for cell in row)}\n"
        
        # Add abundance insights
        response += f"""

## 🌿 Nature's Way Data Insights

### Data Characteristics:
- **Data density**: {len(data)} records available for analysis
- **Column variety**: {len(self._header) if self._header else 0} different data dimensions
- **Reusability potential**: High - data structure cached for collective benefit

### Abundant Sharing Opportunities:
1. **Column analysis**: Headers reveal data relationships and patterns
2. **Data validation**: Structure assessment available for quality checks
3. **Format flexibility**: Data available in both list and dictionary formats
4. **Collective intelligence**: Data insights contribute to system knowledge base

### Recommended Next Steps:
- Use data for analysis, visualization, or further processing
- Share structural insights with other agents for similar file types
- Consider data validation and cleaning if needed
- Apply statistical analysis or pattern recognition as appropriate

## 📈 Collective Contribution
This CSV analysis has been completed with Vibe Coder principles:
- Data made abundantly accessible in requested format
- Structural insights shared for collective benefit
- Processing optimized for reuse and collaboration
- Knowledge contributed without expectation of recognition

*Ready for further collaborative analysis and abundant sharing.*
"""
        
        return response

    def get_last_file_summary(self) -> Dict:
        """Get summary of last processed file for collective knowledge sharing."""
        return self._last_file_info

    def analyze_csv_structure(self, file_path: str, sample_rows: int = 5) -> str:
        """Analyze CSV structure without full data loading - for abundance sharing."""
        try:
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                
                # Get header
                header = next(reader)
                
                # Sample some rows for analysis
                sample_data = []
                for i, row in enumerate(reader):
                    if i >= sample_rows:
                        break
                    sample_data.append(row)
                
                analysis = f"""
# CSV Structure Analysis (Abundant Sharing)
*File: {file_path}*

## Quick Structure Overview:
- **Columns**: {len(header)}
- **Column Names**: {', '.join(header)}
- **Sample Rows**: {len(sample_data)}

## Data Type Inference:
"""
                
                # Basic data type inference
                for i, col_name in enumerate(header):
                    sample_values = [row[i] if i < len(row) else '' for row in sample_data if row]
                    if sample_values:
                        # Simple type inference
                        if all(val.isdigit() for val in sample_values if val):
                            data_type = "Integer"
                        elif all(val.replace('.', '').replace('-', '').isdigit() for val in sample_values if val):
                            data_type = "Float/Decimal"
                        else:
                            data_type = "Text/String"
                        
                        analysis += f"- **{col_name}**: {data_type}\n"
                
                analysis += "\n*Structure analysis shared abundantly for collective benefit*"
                return analysis
                
        except Exception as e:
            return f"Structure analysis error: {str(e)}"
