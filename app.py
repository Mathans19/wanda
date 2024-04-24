from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Attendance(db.Model):
    student_id = db.Column(db.String(20), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, primary_key=True)
    period1 = db.Column(db.Boolean, default=False)
    period2 = db.Column(db.Boolean, default=False)
    period3 = db.Column(db.Boolean, default=False)
    period4 = db.Column(db.Boolean, default=False)
    period5 = db.Column(db.Boolean, default=False)
    period6 = db.Column(db.Boolean, default=False)
    period7 = db.Column(db.Boolean, default=False)

@app.route('/mark-attendance', methods=['POST'])
def mark_attendance():
    data = request.json
    student_id = data['student_id']
    student_name = data['student_name']
    current_date = datetime.now().date()
    current_time = datetime.now().time()
    
    periods = [
        {"start_time": datetime.strptime('08:00:00', '%H:%M:%S').time(), "end_time": datetime.strptime('09:00:00', '%H:%M:%S').time()},
        {"start_time": datetime.strptime('09:00:00', '%H:%M:%S').time(), "end_time": datetime.strptime('10:00:00', '%H:%M:%S').time()},
        {"start_time": datetime.strptime('10:00:00', '%H:%M:%S').time(), "end_time": datetime.strptime('11:00:00', '%H:%M:%S').time()},
        {"start_time": datetime.strptime('11:00:00', '%H:%M:%S').time(), "end_time": datetime.strptime('12:00:00', '%H:%M:%S').time()},
        {"start_time": datetime.strptime('13:00:00', '%H:%M:%S').time(), "end_time": datetime.strptime('14:00:00', '%H:%M:%S').time()},
        {"start_time": datetime.strptime('14:00:00', '%H:%M:%S').time(), "end_time": datetime.strptime('15:00:00', '%H:%M:%S').time()},
        {"start_time": datetime.strptime('15:00:00', '%H:%M:%S').time(), "end_time": datetime.strptime('20:00:00', '%H:%M:%S').time()}
    ]
    
    period_found = False
    for i, period in enumerate(periods, start=1):
        if current_time >= period["start_time"] and current_time <= period["end_time"]:
            period_found = True
            break
    
    if not period_found:
        return jsonify({'message': 'No period found for the current time'}), 400
    
    existing_record = Attendance.query.filter_by(student_id=student_id, date=current_date).first()
    if existing_record:
        # Student already marked attendance for the current date, update attendance for the appropriate period
        for i, period in enumerate(periods, start=1):
            if current_time >= period["start_time"] and current_time <= period["end_time"]:
                setattr(existing_record, f"period{i}", True)
                db.session.commit()
                return jsonify({'message': f'Attendance marked successfully for period {i}'}), 200
        return jsonify({'message': 'Student already marked attendance for the current date'}), 400
    else:
        # Student not marked attendance for the current date, insert new attendance record
        new_attendance = Attendance(student_id=student_id, name=student_name, date=current_date)
        for i, period in enumerate(periods, start=1):
            if current_time >= period["start_time"] and current_time <= period["end_time"]:
                setattr(new_attendance, f"period{i}", True)
                break
        db.session.add(new_attendance)
        db.session.commit()
        return jsonify({'message': 'Attendance marked successfully'}), 200

if __name__ == '__main__':
    # Get the port from the PORT environment variable, default to 5000 if not set
    port = int(os.environ.get("PORT", 5000))
    # Run the app with the host as 0.0.0.0 to accept connections from outside
    app.run(host='0.0.0.0', port=port, debug=True)
