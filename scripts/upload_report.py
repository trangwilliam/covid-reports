import os

from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext

from dotenv import load_dotenv

def upload_report(site: str, localpath: str, remotepath: str) -> None:
    """
    Uploads a file to an LA County Metro SharePoint site

    Args:
        site (string): SharePoint site to upload to
        localpath (string): Path of file to upload
        remotepath (string): Location to upload file to
    """

    # load_dotenv('.env')

    # Get user variables
    username = os.getenv('METRO_EMAIL')
    password = os.getenv('METRO_PASSWORD')
    base_url = os.getenv('SHAREPOINT_URL')

    site_url = f'{base_url}sites/{site}'
    
    # Creates an authentication token for SharePoint site
    ctx_auth = AuthenticationContext(site_url)
    ctx_auth.acquire_token_for_user(username, password)

    # Log in to SharePoint site
    ctx = ClientContext(site_url, ctx_auth)

    # Convert file into binary file
    with open(localpath, 'rb') as f:
        file_content = f.read()

    # Upload the file to SharePoint
    directory, name = os.path.split(remotepath)
    ctx.web.get_folder_by_server_relative_url(directory).upload_file(name, file_content).execute_query()