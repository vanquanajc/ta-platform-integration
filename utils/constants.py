JOBS = [
    'General Accountant', 'Accounts Payable Specialist', 'Accounts Receivable Specialist', 'Chief Accountant',
    'Accounts Payable Leader', 'Business Development Strategy Executive', 'Business Development Strategy Supevisor',
    'Business Development Strategy Leader', 'General Admin Executive', 'Senior Business Development Manager',
    'Business Development Supervisor', 'Business Development Specialist', 'Business Development Executive',
    'Business Development Leader', 'Data Engineer', 'Data Scientist', 'Data Analyst', 'BI Manager', 'BI Leader', 'CEO',
    'Recruitment Officer', 'Content Executive', 'Growth Executive', 'Event Executive', 'PR Executive',
    'Digital Marketing Executive', 'Graphic Designer', 'Marketing Executive', 'Marketing Operations Executive',
    'Marketing Specialist', 'Content Specialist', 'PR Specialist', 'Marketing Operations Specialist',
    'Growth Specialist', 'Event Specialist', 'Digital Marketing Specialist', 'Marketing Manager', 'Media Supervisor',
    'Marketing Operations Supervisor', 'Graphic Design Leader', 'Content Leader', 'Digital Marketing Leader',
    'Marketing Leader', 'Marketing Operations Leader', 'Key Account Specialist', 'Key Account Executive',
    'Key Account Officer', 'Key Account Leader', 'Operations Officer', 'Operations Executive', 'Operations Specialist',
    'Operations Leader', 'Customer Services Specialist', 'Customer Services Officer', 'Customer Services Executive',
    'Customer Services Supervisor', 'Customer Services Leader', 'Field Sales Specialist', 'Telesales Specialist',
    'Field Sales Executive', 'Telesale Officer', 'Telesales Executive', 'Business Analyst', 'Operations Supervisor',
    'Operations Director', 'Operations Manager', 'Key Account Supervisor', 'Training Specialist', 'Training Executive',
    'Quality Control Specialist', 'Quality Control Executive', 'Risk Management Specialist',
    'Risk Management Executive', 'Nhân viên Văn hóa nội bộ'
]
JOBS_REGEX = '|'.join(JOBS)

CITY = ['HN', 'Hà Nội', 'HCM', 'Hồ Chí Minh', 'SG', 'Sài Gòn', 'SGN', 'HAN']
CITY_REGEX = '|'.join(CITY)

CODE_REGEX = ''

PHONE_REGEX = r'(0|84|\+84)[-.\s]?\d{1,3}[-.\s]?\d{2,4}[-.\s]?\d{2,4}[-.\s]?\d{2,4}'

SOURCE_DICT = {
    "iappvnco@gmail.com": "AhaMove Website",
    "info@tuyendungtopcv.com": "TopCV",
    "resumes@mail.careerbuilder.vn": "CareerBuilder"
}