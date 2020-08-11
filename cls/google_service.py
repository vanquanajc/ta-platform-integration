import pandas as pd
import pickle
import os
import base64
import json

from oauth2client import client
from googleapiclient.discovery import build
from google.auth.transport.requests import Request


class GoogleService:
    def __init__(self, token: str = None, _service: str = None):
        self.token = token
        self._service = _service
        self.service = None

    def build_service(self, _service: str = None, token: str = None):
        """
        Build Google Sheet service to interact with Spreadsheets.

        :param _service: {'sheets', 'gmail'}
        :param token: Google account token (Default None)
        :type token: str
        :return:
        """

        token = self.token if not token else token
        _service = self._service if not _service else _service
        assert token, "Must provide a Google account token"
        assert (_service == 'sheets' or _service == 'gmail'), "Service must be either 'sheets' or 'gmail'"
        if _service == 'gmail':
            version = 'v1'
        elif _service == 'sheets':
            version = 'v4'
        else:
            version = None

        try:
            if os.path.exists(token):
                with open(token, 'rb') as token:
                    credentials = pickle.load(token)
                if not credentials or not credentials.valid:
                    if credentials and credentials.expired and credentials.refresh_token:
                        credentials.refresh(Request())
                self.service = build(_service, version, credentials=credentials)
            elif isinstance(token, str):
                credentials = client.Credentials.new_from_json(token)
                self.service = build(_service, version, credentials=credentials)
        except Exception as err:
            print(err)

    def get_email_list(self, label_ids: list = None, get_all: bool = False) -> list:
        """
        Get a list of email ids

        :param label_ids: Filter email by label
        :param get_all: Return all email ids, else 1 page only {True, False}
        :return: List of email ids
        """
        if label_ids is None:
            label_ids = ['UNREAD']
        if not self.service:
            self.build_service('gmail')

        messages = []
        payload = self.service.users().messages().list(userId='me', labelIds=label_ids).execute()
        if 'messages' in payload:
            messages.extend(payload['messages'])
        if get_all:
            while 'nextPageToken' in payload:
                page_token = payload.get('nextPageToken')
                payload = self.service.users().messages().list(userId='me', labelIds=label_ids,
                                                               pageToken=page_token).execute()
                messages.extend(payload['messages'])
        output = [i.get('id') for i in messages]
        return output

    def read_email(self, _id, _format, metadata=None) -> dict:
        """

        :param _id: Message ID
        :type _id: str
        :param _format: Define how to parse the message {'raw', 'full', 'metadata'}
        :type _format: str
        :param metadata: If format is metadata, list the data want to get.
        :type metadata: list
        :return: dict
        """

        assert (_format == "raw" or _format == "full" or _format == "metadata")
        if not self.service:
            self.build_service('gmail')

        if _format == "raw":
            results = self.service.users().messages().get(userId='me', id=_id, format=_format).execute()
            encoded = results.get('raw')
            output = base64.urlsafe_b64decode(encoded).decode()
        elif _format == "full":
            payload = self.service.users().messages().get(userId='me', id=_id).execute()
            output = {"mail_id": _id}
            for part in payload['payload']['headers']:
                if part.get('name') == 'Date':
                    output['date'] = pd.to_datetime(part.get('value'))\
                        .tz_convert('Asia/Bangkok').strftime('%Y-%m-%d %H:%M:%S')
                elif part.get('name') == 'From':
                    output['from_mail'] = part.get('value').split('<')[-1].replace('>', '').strip()
                elif part.get('name') == 'Reply-To':
                    output['reply_to'] = part.get('value')
                elif part.get('name') == 'Subject':
                    output['subject'] = part.get('value')
            try:
                body = base64.urlsafe_b64decode(payload['payload']['parts'][0]['body']['data'].encode('UTF-8')).decode()
            except KeyError:
                body = payload['snippet']
            output['body'] = body
        elif _format == "metadata":
            metadata = ['Subject', 'From', 'Reply-To', 'Date'] if metadata is None else metadata
            results = self.service.users().messages().get(userId='me', id=_id,
                                                          format=_format, metadataHeaders=metadata).execute()
            output = results.get('payload').get('headers')
        else:
            output = None

        return output

    def remove_labels(self, ids: list, label_ids: list = None):
        assert isinstance(ids, list)
        assert isinstance(label_ids, list)
        self.service = self.build_service('gmail') if not self.service else self.service

        if label_ids is None:
            label_ids = ['UNREAD']
        for batch in range((len(ids) // 1000) + 1):
            sub_ids = ids[batch*1000:(batch+1)*1000]
            if len(sub_ids) > 0:
                self.service.users().messages().batchModify(userId='me', ids=sub_ids, removeLabelIds=label_ids)

    def get_attachment(self, _id: str, attachment_id: str, path: str = None):
        """
        Download the attachment of email message

        :param _id: Message ID
        :type _id: str
        :param attachment_id: ID of the attachment, get from read_email full format
        :type attachment_id: str
        :param path: Save path
        :type path: str
        :return: None
        """

        self.service = self.build_service('gmail') if not self.service else self.service

        r = self.service.users().messages().attachments.get(userId='me', id=_id, attachmentId=attachment_id)
        file_data = json.loads(r.text).get('data')
        file_data = base64.urlsafe_b64decode(file_data.encode('UTF-8'))
        if path:
            with open(path, 'wb') as f:
                f.write(file_data)

    def play_with_sheet(self, spreadsheet_id=None, _range=None, method='read', dataframe=None, sheet_name=None,
                        num_row=None, num_col=None):
        """
        Interact with Google Sheet.

        :param spreadsheet_id: Sheet ID
        :type spreadsheet_id: str
        :param _range: Range to interact
        :type _range: str
        :param method: {'read', 'clear', 'write', 'append', 'new_sheet'}
        :type method: str
        :param dataframe: For "write" and "append" method. None for all other methods. (Default None)
        :type dataframe: pd.DataFrame
        :param sheet_name: For "newSheet" method. None for all others (Default None)
        :type sheet_name: str
        :param num_row: For "newSheet" method. None for all others (Default None)
        :type num_row: int
        :param num_col: For "newSheet" method. None for all others (Default None)
        :type num_col: int
        :return: DataFrame or Response
        """

        if not self.service:
            self.build_service('sheets')

        if method == 'read':
            result = self.service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=_range).execute()
            values = result.get('values', [])
            df = pd.DataFrame(values)
            df = df.iloc[1:].rename(columns=df.iloc[0])
            return df
        elif method == 'write':
            values = [dataframe.columns.values.astype(str).tolist()]
            values += dataframe.astype(str).values.tolist()
            data = [
                {
                    'range': _range,
                    'values': values,
                }
            ]
            body = {
                'valueInputOption': 'USER_ENTERED',
                'data': data
            }
            response = self.service.spreadsheets().values().batchUpdate(spreadsheetId=spreadsheet_id,
                                                                        body=body).execute()
        elif method == 'clear':
            body = {
                'ranges': _range
            }
            response = self.service.spreadsheets().values().batchClear(spreadsheetId=spreadsheet_id,
                                                                       body=body).execute()
        elif method == 'append' and len(dataframe) > 0:
            body = {
                'values': dataframe.astype(str).values.tolist()
            }
            response = self.service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=_range,
                                                                   valueInputOption='RAW',
                                                                   insertDataOption='INSERT_ROWS', body=body).execute()
        elif method == 'new_sheet':
            body = {
                'requests': [
                    {
                        "addSheet": {
                            "properties": {
                                "title": sheet_name,
                                "gridProperties": {
                                    "rowCount": num_row,
                                    "columnCount": num_col
                                }
                            }
                        }
                    }
                ]
            }
            response = self.service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()
        else:
            response = None

        return response
