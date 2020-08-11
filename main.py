from cls.google_service import GoogleService
from cls.email_parser import EmailParser

import pandas as pd


e = GoogleService(token='./ta_token.pickle', _service='gmail')
p = EmailParser(e)
g = GoogleService(token='./token.pickle', _service='sheets')
unread = e.get_email_list()
new_applicant = []
for email_id in unread:
    print(email_id)
    email_data = e.read_email(email_id, _format='full')
    data = p.parse_email(email_data)
    if data and data.get('position') is not None:
        del data['body']
        del data['from_mail']
        del data['subject']
        if data.get('reply_to'):
            del data['reply_to']
        new_applicant.append(data)
new_applicant_df = pd.DataFrame(new_applicant)
g.play_with_sheet(spreadsheet_id='1rjFGLtga3jUR6z5lsnKQTm4URR_A7lZIW7lHmIftnIo', _range='Sheet1',
                  method='write', dataframe=new_applicant_df)