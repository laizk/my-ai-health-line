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
    emergency_contact TEXT,
    login_username VARCHAR(100),
    login_password VARCHAR(255)
);

CREATE TABLE carers (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    full_name VARCHAR(255) NOT NULL,
    relationship_to_patient VARCHAR(100),
    contact_number VARCHAR(50),
    notes TEXT,
    login_username VARCHAR(100),
    login_password VARCHAR(255)
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

CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
