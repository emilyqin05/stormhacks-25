import calendar_module
import json
# Initialize the calendar manager
cal_manager = calendar_module.CalendarManager()

# Define your pool of interviewers
interviewers = [
    {
        'id': 'int_001',
        'name': 'Emily Qin',
        'email': '123emilyqin@gmail.com',
        'slack_id': 'U1234ABCD',
        'slack_email': 'emily@company.com',
        'zoom_link': 'https://zoom.us/j/emily-personal-room',
        'role': 'Senior Engineer'
    },
    {
        'id': 'int_002',
        'name': 'Simon',
        'email': 'candidateagent9@gmail.com',
        'slack_id': 'U5678EFGH',
        'slack_email': 'agent@company.com',
        'zoom_link': 'https://zoom.us/j/agent-personal-room',
        'role': 'Tech Lead'
    },
    {
        'id': 'int_003',
        'name': 'Jule',
        'email': 'name@gmail.com',
        'slack_id': 'I5678EFGH',
        'slack_email': 'name@company.com',
        'zoom_link': 'https://zoom.us/j/name-personal-room',
        'role': 'Design Lead'
    }
]

# Find 3 interview slots
interview_slots = cal_manager.find_interview_slots_any_available(
    interviewers=interviewers,
    num_slots=3,
    duration_minutes=60
)

# Result will be in the format you specified
print(json.dumps(interview_slots, indent=2))