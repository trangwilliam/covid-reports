import os, shutil

from datetime import datetime

from create_reports import create_all_reports
from upload_report import upload_report

def delete_reports():
    """
    Deletes 'reports' and 'screenshots' directories
    """

    if os.path.exists('reports'):
        shutil.rmtree('reports', ignore_errors=True)
    if os.path.exists('screenshots'):
        shutil.rmtree('screenshots', ignore_errors=True)

if __name__ == '__main__':
    # Get current date
    day = datetime.today()
    day_formatted = day.strftime('%m.%d.%Y')

    # Variables for SharePoint
    site_path = os.getenv('REPORT_SITE_NAME')
    union_report_ext = os.getenv('UNION_REPORT_EXT')
    filename = f"Union Data Report ({day_formatted}).pdf"

    # Declare paths to upload to and from
    localpath = f'reports/{filename}'
    remotepath = f'{union_report_ext}/{filename}'
    
    # Creates reports
    create_all_reports()

    # Upload reports to SharePoint
    upload_report(site_path, localpath, remotepath)  # type: ignore
    
    # Delete local directories of reports
    delete_reports()
