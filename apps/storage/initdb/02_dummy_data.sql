INSERT INTO doctors (full_name, specialization) VALUES
('Dr. Alice Tan', 'General Practitioner'),
('Dr. Bernard Khoo', 'Cardiology'),
('Dr. Cynthia Lee', 'Pediatrics'),
('Dr. Daniel Ng', 'Orthopedics'),
('Dr. Evelyn Chua', 'Dermatology');

INSERT INTO patients (full_name, birthdate, gender, contact_number, address, emergency_contact) VALUES
('John Lim', '1985-02-14', 'Male', '91234567', 'Bedok, Singapore', 'Maria Lim - 98765432'),
('Sarah Tan', '1991-10-03', 'Female', '98761234', 'Tampines, Singapore', 'Henry Tan - 92342342'),
('Michael Ong', '1972-05-19', 'Male', '90012345', 'Pasir Ris, Singapore', 'Joy Ong - 88992233'),
('Aisha Rahman', '2005-08-12', 'Female', '95671234', 'Sengkang, Singapore', 'Farah Rahman - 93453453'),
('Lucas Wong', '2018-03-21', 'Male', '99887766', 'Yishun, Singapore', 'Linda Wong - 93334444'),
('Grandpa Tan', '1950-07-02', 'Male', '95551111', 'Hougang, Singapore', 'Sarah Tan - 98761234');

INSERT INTO carers (patient_id, full_name, relationship_to_patient, contact_number, notes) VALUES
(3, 'Joy Ong', 'Spouse / Primary Carer', '88992233', 'Supports daily glucose monitoring'),
(4, 'Farah Rahman', 'Mother / Legal Guardian', '93453453', 'Required for consent and follow-ups'),
(5, 'Linda Wong', 'Mother', '93334444', 'Handles clinic visits and medication pickups'),
(4, 'Guardian Team', 'Community Volunteer', '90000001', 'Shared account for minors when parents unavailable'),
(6, 'Sarah Tan', 'Daughter / Carer', '98761234', 'Primary contact for elderly care'),
(4, 'Community Nurse', 'Visiting Nurse', '90000002', 'Covers several assigned patients'),
(5, 'Community Nurse', 'Visiting Nurse', '90000002', 'Covers several assigned patients');

-- Centralized users for all roles (with carer_id)
INSERT INTO users (username, password, role, patient_id, doctor_id, carer_id) VALUES
('admin', 'admin123', 'admin', NULL, NULL, NULL),
('dr_alice', 'doctor123', 'doctor', NULL, 1, NULL),
('dr_bernard', 'doctor123', 'doctor', NULL, 2, NULL),
('john', 'john123', 'patient', 1, NULL, NULL),
('sarah', 'sarah123', 'patient', 2, NULL, NULL),
('michael', 'michael123', 'patient', 3, NULL, NULL),
('aisha', 'aisha123', 'patient', 4, NULL, NULL),
('lucas', 'lucas123', 'patient', 5, NULL, NULL),
('grandpa', 'grandpa123', 'patient', 6, NULL, NULL),
('guardian', 'guardian123', 'carer', NULL, NULL, 4), -- Community volunteer for patients 4 & 6
('joy', 'joy123', 'carer', NULL, NULL, 1),          -- Spouse of patient 3
('farah', 'farah123', 'carer', NULL, NULL, 2),       -- Mother of patient 4
('linda', 'linda123', 'carer', NULL, NULL, 3),       -- Mother of patient 5
('nurse', 'nurse123', 'carer', NULL, NULL, 6);       -- Community nurse covering patients 4 & 5

-- Map users to the patients they can access
INSERT INTO user_patient_access (user_id, patient_id)
SELECT users.id, patients.id FROM users JOIN patients ON 1=0;

-- Patients map to themselves
INSERT INTO user_patient_access (user_id, patient_id) VALUES
((SELECT id FROM users WHERE username='john'), 1),
((SELECT id FROM users WHERE username='sarah'), 2),
((SELECT id FROM users WHERE username='michael'), 3),
((SELECT id FROM users WHERE username='aisha'), 4),
((SELECT id FROM users WHERE username='lucas'), 5),
((SELECT id FROM users WHERE username='grandpa'), 6);

-- Carers mapped to their patients
INSERT INTO user_patient_access (user_id, patient_id) VALUES
((SELECT id FROM users WHERE username='joy'), 3),
((SELECT id FROM users WHERE username='farah'), 4),
((SELECT id FROM users WHERE username='linda'), 5),
((SELECT id FROM users WHERE username='guardian'), 4),
((SELECT id FROM users WHERE username='guardian'), 6),
((SELECT id FROM users WHERE username='nurse'), 4),
((SELECT id FROM users WHERE username='nurse'), 5);

INSERT INTO conditions (patient_id, condition_name, severity_level, diagnosed_date) VALUES
(1, 'High Blood Pressure', 'Moderate', '2021-06-10'),
(2, 'Eczema', 'Mild', '2023-01-15'),
(3, 'Type 2 Diabetes', 'Severe', '2019-11-20'),
(4, 'Asthma', 'Moderate', '2010-03-10'),
(5, 'Recurrent Fever (Pediatric)', 'Moderate', '2024-02-12');

INSERT INTO appointments (patient_id, doctor_id, appointment_date, status) VALUES
(1, 1, '2025-01-10 09:00:00', 'completed'),
(2, 5, '2025-01-12 11:00:00', 'completed'),
(3, 2, '2025-01-15 14:30:00', 'pending'),
(4, 3, '2025-01-20 10:00:00', 'approved'),
(5, 3, '2025-01-22 08:30:00', 'pending');

INSERT INTO referrals (appointment_id, referred_to_specialization, reason, status) VALUES
(1, 'Cardiology', 'Follow-up for hypertension', 'pending'),
(2, 'Dermatology', 'Chronic eczema evaluation', 'completed');

INSERT INTO notifications (patient_id, message, status) VALUES
(1, 'Your referral to Cardiology is pending approval.', 'pending'),
(2, 'Your Dermatology referral has been approved.', 'sent'),
(3, 'Your appointment is still pending.', 'pending'),
(4, 'Your appointment is approved. Please attend on time.', 'sent'),
(5, 'Your appointment request has been received.', 'pending');

-- Medication schedules (dummy)
INSERT INTO medication_schedules (patient_id, medication_name, dosage, frequency, start_date, end_date, intake_time, status, remarks) VALUES
(1, 'Lisinopril', '10mg', 'Once daily', '2025-01-01', '2025-03-01', '08:00:00', 'taken', 'No issues, BP improving'),
(3, 'Metformin', '500mg', 'Twice daily', '2025-01-05', '2025-04-05', '08:00:00', 'pending', 'Reminder sent this morning'),
(3, 'Metformin', '500mg', 'Twice daily', '2025-01-05', '2025-04-05', '20:00:00', 'missed', 'Patient reported nausea, follow up needed'),
(4, 'Salbutamol Inhaler', '2 puffs', 'As needed', '2025-01-01', '2025-02-28', '09:00:00', 'taken', 'Timed for morning activity'),
(5, 'Paracetamol', '250mg', 'Every 6 hours', '2025-01-20', '2025-01-27', '06:00:00', 'pending', 'Guardian to confirm intake'),
(5, 'Paracetamol', '250mg', 'Every 6 hours', '2025-01-20', '2025-01-27', '12:00:00', 'pending', 'Guardian to confirm intake'),
(5, 'Paracetamol', '250mg', 'Every 6 hours', '2025-01-20', '2025-01-27', '18:00:00', 'taken', 'Dose taken at clinic'),
(2, 'Amoxicillin', '500mg', 'Three times daily', '2025-02-01', '2025-02-10', '08:00:00', 'pending', 'Start of antibiotic course'),
(2, 'Amoxicillin', '500mg', 'Three times daily', '2025-02-01', '2025-02-10', '14:00:00', 'pending', 'Start of antibiotic course'),
(2, 'Amoxicillin', '500mg', 'Three times daily', '2025-02-01', '2025-02-10', '20:00:00', 'pending', 'Start of antibiotic course'),
(6, 'Atorvastatin', '20mg', 'Once daily', '2025-02-01', '2025-08-01', '21:00:00', 'pending', 'Monitor lipids quarterly');
