import pandas as pd
from pathlib import Path


class ExcelGenerator:
    def __init__(self):
        self.columns = ['User', 'Review', 'Package ID', 'Rating', 'Date', 'Time']
    
    def generate(self, reviews: list, filepath: Path):
        """
        Generate Excel file from reviews list.
        
        Args:
            reviews: List of review dictionaries
            filepath: Path where to save the Excel file
        """
        try:
            # Create DataFrame with correct column order
            df = pd.DataFrame(reviews)
            
            # Ensure columns exist and are in correct order
            df = df[self.columns]
            
            # Write to Excel
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Reviews')
                
                # Get the workbook and worksheet
                workbook = writer.book
                worksheet = writer.sheets['Reviews']
                
                # Auto-adjust column widths
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    
                    adjusted_width = min(max_length + 2, 50)  # Cap at 50
                    worksheet.column_dimensions[column_letter].width = adjusted_width
                
                # Freeze header row
                worksheet.freeze_panes = 'A2'
            
            return filepath
        
        except Exception as e:
            raise Exception(f"Failed to generate Excel file: {str(e)}")
