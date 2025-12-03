from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text, TIMESTAMP, Time
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class UserAccount(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String)  # admin, doctor, patient, carer
    patient_id = Column(Integer, ForeignKey("patients.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    carer_id = Column(Integer, ForeignKey("carers.id"))

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String)
    birthdate = Column(Date)
    gender = Column(String)
    contact_number = Column(String)
    address = Column(Text)
    emergency_contact = Column(Text)

class Carer(Base):
    __tablename__ = "carers"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    full_name = Column(String)
    relationship_to_patient = Column(String)
    contact_number = Column(String)
    notes = Column(Text)

class UserPatientAccess(Base):
    __tablename__ = "user_patient_access"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    patient_id = Column(Integer, ForeignKey("patients.id"))

class MedicationSchedule(Base):
    __tablename__ = "medication_schedules"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    medication_name = Column(String)
    dosage = Column(String)
    frequency = Column(String)
    start_date = Column(Date)
    end_date = Column(Date)
    intake_time = Column(Time)
    status = Column(String)  # pending, taken, missed
    remarks = Column(Text)

class ConversationSessionConcierge(Base):
    __tablename__ = "conversation_sessions_concierge"

    id = Column(Integer, primary_key=True)
    session_id = Column(String, unique=True, index=True)
    app_name = Column(String)
    user_id = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())

class ConversationMessageConcierge(Base):
    __tablename__ = "conversation_messages_concierge"

    id = Column(Integer, primary_key=True)
    session_id = Column(String, ForeignKey("conversation_sessions_concierge.session_id", ondelete="CASCADE"))
    role = Column(String)   # user | assistant
    content = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

class ConversationSessionDoctor(Base):
    __tablename__ = "conversation_sessions_doctor"

    id = Column(Integer, primary_key=True)
    session_id = Column(String, unique=True, index=True)
    app_name = Column(String)
    user_id = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())

class ConversationMessageDoctor(Base):
    __tablename__ = "conversation_messages_doctor"

    id = Column(Integer, primary_key=True)
    session_id = Column(String, ForeignKey("conversation_sessions_doctor.session_id", ondelete="CASCADE"))
    role = Column(String)   # user | assistant
    content = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

class LoginSession(Base):
    __tablename__ = "login_sessions"

    id = Column(Integer, primary_key=True)
    session_token = Column(String, unique=True, index=True)
    username = Column(String)
    full_name = Column(String)
    role = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())
    last_seen = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

class Condition(Base):
    __tablename__ = "conditions"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    condition_name = Column(String)
    severity_level = Column(String)
    diagnosed_date = Column(Date)

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    specialization = Column(String)

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    appointment_date = Column(TIMESTAMP)
    status = Column(String)

class Referral(Base):
    __tablename__ = "referrals"

    id = Column(Integer, primary_key=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id"))
    referred_to_specialization = Column(String)
    reason = Column(Text)
    status = Column(String)
