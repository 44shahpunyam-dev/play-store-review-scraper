import pandas as pd
from pathlib import Path
import re


class ExcelGenerator:
    def __init__(self):
        self.columns = ['User', 'Review', 'Package ID', 'Rating', 'Date', 'Time']
    
    @staticmethod
    def get_filename(app_name: str, hint: str, from_date: str, to_date: str) -> str:
        """
        Format filename as: AppName_Hint_Date.xlsx
        """
        clean_app = re.sub(r'[\\/*?:"<>|\0]', '_', app_name).strip()
        clean_app = re.sub(r'\s+', '_', clean_app)
        
        date_part = from_date if from_date == to_date else f"{from_date}_to_{to_date}"
        
        if hint and hint.strip():
            clean_hint = re.sub(r'[\\/*?:"<>|\0]', '_', hint.strip())
            clean_hint = re.sub(r'\s+', '_', clean_hint)
            return f"{clean_app}_{clean_hint}_{date_part}.xlsx"
        else:
            return f"{clean_app}_{date_part}.xlsx"

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
