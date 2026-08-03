import io
import base64
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.graphics.barcode import code128, qr
from pypdf import PdfReader, PdfWriter
import json

def render_overlay_pdf(canvas_json, order_data, width_mm=101.6, height_mm=152.4):
    """
    Renders the overlay elements into a transparent PDF in memory.
    1 mm = 2.83465 pt natively in ReportLab when using mm unit.
    """
    packet = io.BytesIO()
    
    # create a new PDF with Reportlab
    c = canvas.Canvas(packet, pagesize=(width_mm * mm, height_mm * mm))
    
    # For a real implementation we would register fonts:
    # from reportlab.pdfbase.ttfonts import TTFont
    # from reportlab.pdfbase import pdfmetrics
    # pdfmetrics.registerFont(TTFont('Inter', 'static/fonts/Inter-Regular.ttf'))
    
    # canvas_json example: {"objects": [{"type": "text", "left": 10, "top": 10, "text": "{{buyer_name}}", "fontSize": 12}]}
    objects = canvas_json.get('objects', [])
    
    for obj in objects:
        obj_type = obj.get('type')
        x_mm = obj.get('left', 0)
        y_mm = obj.get('top', 0)
        
        # ReportLab origin is bottom-left, Fabric.js origin is top-left.
        # So y_reportlab = height_mm - y_fabric
        y_pt = (height_mm - y_mm) * mm
        x_pt = x_mm * mm
        
        if obj_type == 'text' or obj_type == 'i-text':
            text_val = obj.get('text', '')
            # Very basic merge field replacement
            for key, val in order_data.items():
                text_val = text_val.replace(f"{{{{{key}}}}}", str(val))
                
            font_size = obj.get('fontSize', 12)
            c.setFont("Helvetica", font_size) # Fallback if Inter fails
            c.drawString(x_pt, y_pt - font_size, text_val) # adjust Y for baseline
            
        elif obj_type == 'barcode-128':
            value = obj.get('value', '123456')
            for key, val in order_data.items():
                value = value.replace(f"{{{{{key}}}}}", str(val))
            
            # Minimum enforced module width 0.25mm (~1 pt) for 300 DPI scanners
            bc = code128.Code128(value, barHeight=10*mm, barWidth=0.25*mm)
            bc.drawOn(c, x_pt, y_pt - 10*mm)
            
        elif obj_type == 'qrcode':
            value = obj.get('value', 'https://daraz.pk')
            for key, val in order_data.items():
                value = value.replace(f"{{{{{key}}}}}", str(val))
            # Create QR
            qr_code = qr.QrCodeWidget(value)
            qr_code.barWidth = 20 * mm
            qr_code.barHeight = 20 * mm
            # qr_code.drawOn(c, x_pt, y_pt - 20*mm) # Would use drawing mechanics
            
    c.save()
    packet.seek(0)
    return packet

def merge_daraz_label_with_overlay(daraz_base64_pdf, overlay_pdf_stream):
    """
    Takes a base64 encoded Daraz PDF and merges it with the ReportLab overlay PDF.
    Returns a BytesIO stream of the merged PDF.
    """
    # 1. Decode Daraz PDF
    daraz_pdf_bytes = base64.b64decode(daraz_base64_pdf)
    daraz_stream = io.BytesIO(daraz_pdf_bytes)
    
    # 2. Read both
    daraz_reader = PdfReader(daraz_stream)
    overlay_reader = PdfReader(overlay_pdf_stream)
    
    writer = PdfWriter()
    
    # 3. Merge pages
    # Usually Daraz sends 1 page per label. 
    # If there are multiple pages, we might need multiple overlays or just apply to the first.
    for i in range(len(daraz_reader.pages)):
        page = daraz_reader.pages[i]
        
        # If we have an overlay for this page
        if i < len(overlay_reader.pages):
            overlay_page = overlay_reader.pages[i]
            page.merge_page(overlay_page)
            
        writer.add_page(page)
        
    output_stream = io.BytesIO()
    writer.write(output_stream)
    output_stream.seek(0)
    
    return output_stream
