from celery import shared_task
from .models import Report
import time


@shared_task(bind=True)
def generate_report_task(self, report_id):
    try:
        report = Report.objects.get(id=report_id)
        report.status = Report.Status.PROCESSING
        report.save(update_fields=['status'])

        time.sleep(5)

        report.status = Report.Status.COMPLETED
        report.file_path = f'/media/reports/report_{report_id}.pdf'
        report.save(update_fields=['status', 'file_path'])
        return f'Report {report_id} generated'
    except Exception as e:
        report = Report.objects.get(id=report_id)
        report.status = Report.Status.FAILED
        report.save(update_fields=['status'])
        raise e