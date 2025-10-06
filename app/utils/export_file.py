import csv
import os
import pdfplumber # to read pdf
from openpyxl import load_workbook, Workbook
from exceptions.exception import ValidationError

# to work on pdf
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors


class ExportManager:
    def __init__(self, file_name=None, file_type=None):
        self.file_name = file_name
        self.file_type = file_type.lower() if file_type else None
        self._validate()

    def _validate(self):
        ACCEPTED_TYPES = {'.csv', '.xlsx', '.pdf'}

        if not self.file_name:
            raise ValidationError('File name is required.')

        if not self.file_type:
            raise ValidationError('File type is required.')
        
        if self.file_type not in ACCEPTED_TYPES:
            raise ValidationError(f'File type: {self.file_type} not valid. Most include {', '.join(ACCEPTED_TYPES)}')
        
    def export_to_csv(self, data, column_names=None):
        if self.file_type != '.csv':
            raise ValidationError(f"Error expected 'CSV' but got {self.file_type}")
        
        with open(self.file_name, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if column_names:
                writer.writerow(column_names)  # write header
            writer.writedata(data)

    def export_to_excel(self, data, column_names=None):
        wb = Workbook()
        ws = wb.active
        ws.title = "ExportedData"

        # Write column headers
        if column_names:
            ws.append(column_names)

        # Write data rows
        for row in data:
            ws.append(row)

        # Save the Excel file
        wb.save(self.file_name)

    def export_to_pdf(self, data, column_names=None):
        data_list = data
        # Combine headers and data
        if column_names:
            data_list = [column_names] + data
        # Create a PDF document
        pdf_file = "output.pdf"
        doc = SimpleDocTemplate(pdf_file, pagesize=A4)
        elements = []

        # Create a Table
        table = Table(data)

        # Add table style
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),       # Header background
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Header text
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),     # Header font
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ])

        table.setStyle(style)
        elements.append(table)

        # Build the PDF
        doc.build(elements)




    
        
    
        