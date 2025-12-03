CREATE TABLE doctors (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    specialization VARCHAR(255) NOT NULL
);

CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    birthdate DATE NOT NULL,
    gender VARCHAR(10),
    contact_number VARCHAR(50),
    address TEXT,
    emergency_contact TEXT
);

CREATE TABLE carers (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    full_name VARCHAR(255) NOT NULL,
    relationship_to_patient VARCHAR(100),
    contact_number VARCHAR(50),
    notes TEXT
);

CREATE TABLE conditions (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    condition_name VARCHAR(255) NOT NULL,
    severity_level VARCHAR(50),
    diagnosed_date DATE
);

CREATE TABLE appointments (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    doctor_id INTEGER REFERENCES doctors(id),
    appointment_date TIMESTAMP NOT NULL,
    status VARCHAR(50) NOT NULL
);

CREATE TABLE referrals (
    id SERIAL PRIMARY KEY,
    appointment_id INTEGER REFERENCES appointments(id) ON DELETE CASCADE,
    referred_to_specialization VARCHAR(255),
    reason TEXT,
    status VARCHAR(50)
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    patient_id INTEGER REFERENCES patients(id),
    doctor_id INTEGER REFERENCES doctors(id),
    carer_id INTEGER REFERENCES carers(id)
);

CREATE TABLE user_patient_access (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE
);

CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE medication_schedules (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    medication_name VARCHAR(255) NOT NULL,
    dosage VARCHAR(100),
    frequency VARCHAR(100),
    start_date DATE,
    end_date DATE,
    intake_time VARCHAR(50),
    status VARCHAR(20) DEFAULT 'pending', -- pending, taken, missed
    remarks TEXT
);

-- Conversation sessions and messages for AI assistant
CREATE TABLE conversation_sessions_concierge (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    app_name VARCHAR(100),
    user_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE conversation_messages_concierge (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) REFERENCES conversation_sessions_concierge(session_id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,        -- user | assistant
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE conversation_sessions_doctor (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) UNIQUE NOT NULL,
    app_name VARCHAR(100),
    user_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE conversation_messages_doctor (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR(100) REFERENCES conversation_sessions_doctor(session_id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,        -- user | assistant
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE login_sessions (
    id SERIAL PRIMARY KEY,
    session_token VARCHAR(150) UNIQUE NOT NULL,
    username VARCHAR(100) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
