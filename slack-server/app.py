from flask import Flask, request, jsonify, send_from_directory
import os

app = Flask(__name__, static_folder='.', static_url_path='')


@app.get('/book-interview')
def book_interview():
    print("booking interview")
    # data = request.get_json(silent=True) or {}
    # time_str = data.get('time')
    # date_str = data.get('date')

    # if not time_str or not date_str:
    #     return jsonify({"ok": False, "error": "Missing 'time' or 'date'"}), 400

    # TODO: Insert Google Calendar booking logic here using google-api-python-client
    # Example shape you might construct:
    # event = {
    #     "summary": "Interview",
    #     "start": {"dateTime": iso_start, "timeZone": "America/Los_Angeles"},
    #     "end": {"dateTime": iso_end, "timeZone": "America/Los_Angeles"},
    #     "attendees": [{"email": candidate_email}],
    # }
    # calendar.events().insert(calendarId='primary', body=event).execute()

    # Stub success response for now
    return jsonify({
        "ok": True,
        "message": "Your interview has been booked",
        # "received": {"time": time_str, "date": date_str},
    }), 200

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5001, debug=True)