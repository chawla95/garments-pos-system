import os
from pathlib import Path
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from fastapi.responses import FileResponse
import tempfile
from datetime import datetime
import barcode
from barcode.writer import ImageWriter
from io import BytesIO

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_styles()
        
    def setup_styles(self):
        """Setup custom styles for the invoice"""
        self.styles.add(ParagraphStyle(
            name='ShopName',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=6,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='ShopDetails',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=3,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='InvoiceInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=12
        ))
        
        self.styles.add(ParagraphStyle(
            name='TotalRow',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=6,
            fontName='Helvetica-Bold'
        ))
        
        # Add custom style for currency
        self.styles.add(ParagraphStyle(
            name='Currency',
            parent=self.styles['Normal'],
            fontSize=10,
            fontName='Helvetica'
        ))

    def generate_barcode(self, text):
        """Generate a barcode image from text"""
        try:
            # Create Code128 barcode
            code128 = barcode.get('code128', text, writer=ImageWriter())
            
            # Generate barcode image
            barcode_image = code128.render()
            
            # Convert to BytesIO for ReportLab
            img_buffer = BytesIO()
            barcode_image.save(img_buffer, format='PNG')
            img_buffer.seek(0)
            
            return img_buffer
        except Exception as e:
            print(f"Error generating barcode: {e}")
            return None
        
    def generate_invoice_pdf(self, invoice):
        """
        Generate PDF invoice using ReportLab
        
        Args:
            invoice: Invoice object from database
        
        Returns:
            FileResponse with PDF
        """
        try:
            # Create temporary file for PDF
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
                pdf_path = tmp_file.name
            
            # Use A4 page size
            pagesize = A4
            
            # Create PDF document
            doc = SimpleDocTemplate(pdf_path, pagesize=pagesize)
            story = []
            
            # Add header
            story.extend(self.create_header(invoice))
            
            # Add invoice info
            story.extend(self.create_invoice_info(invoice))
            
            # Add items table
            story.extend(self.create_items_table(invoice))
            
            # Add summary
            story.extend(self.create_summary(invoice))
            
            # Build PDF
            doc.build(story)
            
            # Return file response
            filename = f"invoice_{invoice.invoice_number}.pdf"
            return FileResponse(
                path=pdf_path,
                filename=filename,
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
            
        except Exception as e:
            raise Exception(f"Error generating PDF: {str(e)}")
        
    def generate_return_pdf(self, return_record):
        """
        Generate PDF return receipt using ReportLab
        
        Args:
            return_record: Return object from database
        
        Returns:
            FileResponse with PDF
        """
        try:
            # Create temporary file for PDF
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
                pdf_path = tmp_file.name
            
            # Use A4 page size
            pagesize = A4
            
            # Create PDF document
            doc = SimpleDocTemplate(pdf_path, pagesize=pagesize)
            story = []
            
            # Add header
            story.extend(self.create_return_header(return_record))
            
            # Add return info
            story.extend(self.create_return_info(return_record))
            
            # Add items table
            story.extend(self.create_return_items_table(return_record))
            
            # Add summary
            story.extend(self.create_return_summary(return_record))
            
            # Build PDF
            doc.build(story)
            
            # Return file response
            filename = f"return_{return_record.return_number}.pdf"
            return FileResponse(
                path=pdf_path,
                filename=filename,
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
            
        except Exception as e:
            raise Exception(f"Error generating return PDF: {str(e)}")
    
    def create_header(self, invoice):
        """Create invoice header"""
        story = []
        
        # Shop name
        story.append(Paragraph("FASHION GARMENTS", self.styles['ShopName']))
        
        # Shop details
        story.append(Paragraph("123 Fashion Street, Mumbai - 400001", self.styles['ShopDetails']))
        story.append(Paragraph("Phone: +91 98765 43210 | Email: info@fashiongarments.com", self.styles['ShopDetails']))
        story.append(Paragraph("GSTIN: 27ABCDE1234F1Z5", self.styles['ShopDetails']))
        
        story.append(Spacer(1, 20))
        return story
    
    def create_invoice_info(self, invoice):
        """Create invoice information section"""
        story = []
        
        # Customer info
        customer_name = invoice.customer_name or "Walk-in Customer"
        customer_info = f"<b>Invoice To:</b><br/>{customer_name}"
        if invoice.customer_phone:
            customer_info += f"<br/>Phone: {invoice.customer_phone}"
        if invoice.customer_email:
            customer_info += f"<br/>Email: {invoice.customer_email}"
        
        # Invoice details
        invoice_date = invoice.created_at.strftime('%d/%m/%Y')
        invoice_time = invoice.created_at.strftime('%H:%M:%S')
        payment_method = invoice.payment_method or "Cash"
        
        invoice_info = f"<b>Invoice Number:</b> {invoice.invoice_number}<br/>"
        invoice_info += f"<b>Date:</b> {invoice_date}<br/>"
        invoice_info += f"<b>Time:</b> {invoice_time}<br/>"
        invoice_info += f"<b>Payment Method:</b> {payment_method}"
        
        # Create two-column layout
        data = [
            [Paragraph(customer_info, self.styles['InvoiceInfo']), 
             Paragraph(invoice_info, self.styles['InvoiceInfo'])]
        ]
        
        # Calculate column widths based on A4 page width
        page_width = A4[0]
        col_width = page_width / 2 - 12
        table = Table(data, colWidths=[col_width, col_width])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(table)
        
        # Add barcode
        try:
            barcode_buffer = self.generate_barcode(invoice.invoice_number)
            if barcode_buffer:
                # Create barcode image
                barcode_img = Image(barcode_buffer, width=200, height=50)
                story.append(Spacer(1, 10))
                story.append(barcode_img)
                story.append(Paragraph(f"<b>Scan for Returns:</b> {invoice.invoice_number}", self.styles['Normal']))
        except Exception as e:
            print(f"Barcode generation failed: {e}")
            # Continue without barcode
        
        story.append(Spacer(1, 20))
        return story
    
    def create_items_table(self, invoice):
        """Create items table"""
        story = []
        
        # Full table for A4
        headers = ['Sr. No.', 'Product', 'Design No.', 'Size', 'Color', 'MRP', 'Discount', 'Final Price']
        col_widths = [30, 120, 60, 40, 40, 50, 50, 60]
        
        # Table data
        data = [headers]
        
        for i, item in enumerate(invoice.items, 1):
            # Full row for A4
            row = [
                str(i),
                item.product_name,
                item.design_number,
                item.size,
                item.color,
                f"Rs. {item.total_price:.2f}",
                f"Rs. {item.discount_amount:.2f}",
                f"Rs. {item.final_price:.2f}"
            ]
            data.append(row)
        
        # Create table
        table = Table(data, colWidths=col_widths)
        
        # Style the table
        style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]
        table.setStyle(TableStyle(style))
        
        story.append(table)
        story.append(Spacer(1, 20))
        return story
    
    def create_summary(self, invoice):
        """Create invoice summary"""
        story = []
        
        # Summary data
        summary_data = [
            ['Description', 'Amount'],
            ['Total MRP', f"Rs. {invoice.total_mrp:.2f}"],
        ]
        
        if invoice.total_discount > 0:
            summary_data.append(['Total Discount', f"-Rs. {invoice.total_discount:.2f}"])
        
        summary_data.extend([
            ['Final Amount (GST-inclusive)', f"Rs. {invoice.total_final_price:.2f}"],
            ['', ''],  # Empty row for spacing
            ['Base Amount (ex-GST)', f"Rs. {invoice.total_base_amount:.2f}"],
            ['CGST (6%)', f"Rs. {invoice.total_cgst_amount:.2f}"],
            ['SGST (6%)', f"Rs. {invoice.total_sgst_amount:.2f}"],
            ['Total GST', f"Rs. {invoice.total_gst_amount:.2f}"],
            ['', ''],  # Empty row for spacing
            ['GRAND TOTAL', f"Rs. {invoice.total_final_price:.2f}"]
        ])
        
        # Create summary table
        table = Table(summary_data, colWidths=[200, 100])
        
        # Style the summary table
        style = [
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]
        table.setStyle(TableStyle(style))
        
        story.append(table)
        
        # Add notes if any
        if invoice.notes:
            story.append(Spacer(1, 20))
            story.append(Paragraph(f"<b>Notes:</b> {invoice.notes}", self.styles['Normal']))
        
        # Add footer
        story.append(Spacer(1, 30))
        story.append(Paragraph("Thank you for your business!", self.styles['Normal']))
        story.append(Paragraph("This is a computer generated invoice. No signature required.", self.styles['Normal']))
        story.append(Paragraph("For any queries, please contact us at +91 98765 43210", self.styles['Normal']))
        
        return story

    def create_return_header(self, return_record):
        """Create return receipt header"""
        story = []
        
        # Shop name
        story.append(Paragraph("FASHION GARMENTS", self.styles['ShopName']))
        
        # Shop details
        story.append(Paragraph("123 Fashion Street, Mumbai - 400001", self.styles['ShopDetails']))
        story.append(Paragraph("Phone: +91 98765 43210 | Email: info@fashiongarments.com", self.styles['ShopDetails']))
        story.append(Paragraph("GSTIN: 27ABCDE1234F1Z5", self.styles['ShopDetails']))
        
        story.append(Spacer(1, 20))
        return story

    def create_return_info(self, return_record):
        """Create return information section"""
        story = []
        
        # Customer info
        customer_name = return_record.customer_name or "Walk-in Customer"
        customer_info = f"<b>Return To:</b><br/>{customer_name}"
        if return_record.customer_phone:
            customer_info += f"<br/>Phone: {return_record.customer_phone}"
        if return_record.customer_email:
            customer_info += f"<br/>Email: {return_record.customer_email}"
        
        # Return details
        return_date = return_record.created_at.strftime('%d/%m/%Y')
        return_time = return_record.created_at.strftime('%H:%M:%S')
        
        return_info = f"<b>Return Number:</b> {return_record.return_number}<br/>"
        return_info += f"<b>Original Invoice:</b> {return_record.invoice_number}<br/>"
        return_info += f"<b>Date:</b> {return_date}<br/>"
        return_info += f"<b>Time:</b> {return_time}<br/>"
        return_info += f"<b>Return Method:</b> {return_record.return_method}"
        
        # Create two-column layout
        data = [
            [Paragraph(customer_info, self.styles['InvoiceInfo']), 
             Paragraph(return_info, self.styles['InvoiceInfo'])]
        ]
        
        # Calculate column widths based on A4 page width
        page_width = A4[0]
        col_width = page_width / 2 - 12
        table = Table(data, colWidths=[col_width, col_width])
        
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        story.append(table)
        
        # Add barcode
        try:
            barcode_buffer = self.generate_barcode(return_record.return_number)
            if barcode_buffer:
                # Create barcode image
                barcode_img = Image(barcode_buffer, width=200, height=50)
                story.append(Spacer(1, 10))
                story.append(barcode_img)
                story.append(Paragraph(f"<b>Return Number:</b> {return_record.return_number}", self.styles['Normal']))
        except Exception as e:
            print(f"Barcode generation failed: {e}")
            # Continue without barcode
        
        # Add return reason if provided
        if return_record.return_reason:
            story.append(Spacer(1, 10))
            story.append(Paragraph(f"<b>Return Reason:</b> {return_record.return_reason}", self.styles['Normal']))
        
        story.append(Spacer(1, 20))
        return story

    def create_return_items_table(self, return_record):
        """Create return items table"""
        story = []
        
        # Full table for A4
        headers = ['Sr. No.', 'Product', 'Design No.', 'Size', 'Color', 'Original Qty', 'Return Qty', 'Unit Price', 'Return Amount']
        col_widths = [25, 100, 50, 30, 30, 40, 40, 50, 60]
        
        # Table data
        data = [headers]
        
        for i, item in enumerate(return_record.items, 1):
            # Full row for A4
            row = [
                str(i),
                item.product_name,
                item.design_number,
                item.size,
                item.color,
                str(item.original_quantity),
                str(item.return_quantity),
                f"Rs. {item.unit_price:.2f}",
                f"Rs. {item.total_return_price:.2f}"
            ]
            data.append(row)
        
        # Create table
        table = Table(data, colWidths=col_widths)
        
        # Style the table
        style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.red),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.pink),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]
        table.setStyle(TableStyle(style))
        
        story.append(table)
        story.append(Spacer(1, 20))
        return story

    def create_return_summary(self, return_record):
        """Create return summary"""
        story = []
        
        # Summary data
        summary_data = [
            ['Description', 'Amount'],
            ['Total Return Amount', f"Rs. {return_record.total_return_amount:.2f}"],
            ['', ''],  # Empty row for spacing
            ['Base Amount (ex-GST)', f"Rs. {(return_record.total_return_amount - return_record.total_return_gst):.2f}"],
            ['CGST (6%)', f"Rs. {return_record.total_return_cgst:.2f}"],
            ['SGST (6%)', f"Rs. {return_record.total_return_sgst:.2f}"],
            ['Total GST Return', f"Rs. {return_record.total_return_gst:.2f}"],
            ['', ''],  # Empty row for spacing
        ]
        
        # Add return method details
        if return_record.return_method == "CASH":
            summary_data.append(['Cash Refund', f"Rs. {return_record.cash_refund:.2f}"])
        elif return_record.return_method == "WALLET":
            summary_data.append(['Wallet Credit', f"Rs. {return_record.wallet_credit:.2f}"])
        elif return_record.return_method == "STORE_CREDIT":
            summary_data.append(['Store Credit', f"Rs. {return_record.wallet_credit:.2f}"])
        
        summary_data.append(['', ''],)  # Empty row for spacing
        summary_data.append(['TOTAL RETURN AMOUNT', f"Rs. {abs(return_record.total_return_amount):.2f}"])
        
        # Create summary table
        table = Table(summary_data, colWidths=[200, 100])
        
        # Style the summary table
        style = [
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, -1), (-1, -1), colors.red),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
        ]
        table.setStyle(TableStyle(style))
        
        story.append(table)
        
        # Add notes if any
        if return_record.notes:
            story.append(Spacer(1, 20))
            story.append(Paragraph(f"<b>Notes:</b> {return_record.notes}", self.styles['Normal']))
        
        # Add footer
        story.append(Spacer(1, 30))
        story.append(Paragraph("Thank you for your business!", self.styles['Normal']))
        story.append(Paragraph("This is a computer generated return receipt. No signature required.", self.styles['Normal']))
        story.append(Paragraph("For any queries, please contact us at +91 98765 43210", self.styles['Normal']))
        
        return story

# Create global instance
pdf_generator = PDFGenerator() 