import os, shutil

from datetime import datetime

from create_reports import create_all_reports
from upload_report import upload_report
from dotenv import load_dotenv

def delete_reports() -> None:
    """
    Deletes 'reports' and 'screenshots' directories
    """

    if os.path.exists('reports'):
        shutil.rmtree('reports', ignore_errors=True)
    if os.path.exists('screenshots'):
        shutil.rmtree('screenshots', ignore_errors=True)

if __name__ == '__main__':
    # load_dotenv('.env')

    # Get current date
    day = datetime.today()
    day_formatted = day.strftime('%m.%d.%Y')

    # Variables for SharePoint
    site_path = os.getenv('REPORT_SITE_NAME')
    daily_report_ext = os.getenv('DAILY_REPORT_EXT')
    filename = f"Daily COVID Report ({day_formatted}).pdf"

    # Declare paths to upload to and from
    localpath = f'reports/{filename}'
    remotepath = f'{daily_report_ext}/{filename}'
    
    # Creates reports
    create_all_reports()

    # Upload reports to SharePoint
    upload_report(site_path, localpath, remotepath)

    # Delete local directories of reports
    delete_reports()
