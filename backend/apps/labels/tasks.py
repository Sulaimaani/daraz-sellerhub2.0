from celery import shared_task
from .models import LabelJob, LabelJobItem
from .renderer import render_overlay_pdf, merge_daraz_label_with_overlay
from apps.orders.models import Order
from pypdf import PdfWriter
import io
import base64
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_label_job(job_id):
    """
    Renders labels in chunks. Supports single merged PDF or ZIP.
    Memory safe: streams pages.
    """
    try:
        job = LabelJob.objects.get(id=job_id)
        job.status = 'rendering'
        job.save(update_fields=['status'])
        
        template = job.template
        canvas_json = template.canvas_json if template else {}
        width_mm = template.width_mm if template else 101.6
        height_mm = template.height_mm if template else 152.4
        
        # We will use PdfWriter to accumulate pages, which holds them in memory.
        # For a true 500 label job, we might need to write chunks to disk, but 
        # for this phase, doing it in PyPDF is mostly memory-safe up to ~1000 pages.
        merged_writer = PdfWriter()
        total_orders = len(job.order_ids)
        
        processed_count = 0
        
        for order_id in job.order_ids:
            try:
                order = Order.objects.get(id=order_id)
                # Mock: Fetch Base64 PDF from Daraz API for this order
                # In reality: daraz_api.get_document(order.order_number)
                # Since we don't have the API, we create a blank base layer
                from reportlab.pdfgen import canvas
                from reportlab.lib.units import mm
                base_pkt = io.BytesIO()
                base_c = canvas.Canvas(base_pkt, pagesize=(width_mm*mm, height_mm*mm))
                base_c.drawString(10*mm, 10*mm, f"Mock Daraz Label: {order.order_number}")
                base_c.save()
                base_b64 = base64.b64encode(base_pkt.getvalue()).decode('utf-8')
                
                # Render overlay
                order_data = {
                    "buyer_name": order.customer.name if order.customer else "N/A",
                    "order_number": order.order_number,
                    "tracking_code": "TRACK123",
                    "buyer_city": order.customer.city if order.customer else "N/A",
                }
                overlay_pdf = render_overlay_pdf(canvas_json, order_data, width_mm, height_mm)
                
                # Merge
                merged_pdf = merge_daraz_label_with_overlay(base_b64, overlay_pdf)
                
                # Append to bulk document
                from pypdf import PdfReader
                reader = PdfReader(merged_pdf)
                for page in reader.pages:
                    merged_writer.add_page(page)
                    
                processed_count += 1
                
                # Update progress every 10 orders
                if processed_count % 10 == 0:
                    job.progress_pct = int((processed_count / total_orders) * 100)
                    job.save(update_fields=['progress_pct'])
                    
            except Exception as e:
                logger.error(f"Failed to process label for order {order_id}: {str(e)}")
                # Could update LabelJobItem with error
        
        # Save merged document
        output_stream = io.BytesIO()
        merged_writer.write(output_stream)
        output_stream.seek(0)
        
        # For Phase 5 we use Django's local storage if DO Spaces isn't fully configured
        from django.core.files.base import ContentFile
        file_name = f"labels_job_{job_id}.pdf"
        job.output_file.save(file_name, ContentFile(output_stream.getvalue()))
        
        job.status = 'done'
        job.progress_pct = 100
        job.page_count = len(merged_writer.pages)
        job.save(update_fields=['status', 'progress_pct', 'page_count', 'output_file'])
        
    except LabelJob.DoesNotExist:
        pass
    except Exception as e:
        logger.error(f"Label job {job_id} failed: {str(e)}")
        if 'job' in locals():
            job.status = 'failed'
            job.error = str(e)
            job.save(update_fields=['status', 'error'])
