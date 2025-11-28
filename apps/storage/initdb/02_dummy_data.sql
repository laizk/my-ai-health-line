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
('Lucas Wong', '2018-03-21', 'Male', '99887766', 'Yishun, Singapore', 'Linda Wong - 93334444');

INSERT INTO carers (patient_id, full_name, relationship_to_patient, contact_number, notes) VALUES
(3, 'Joy Ong', 'Spouse / Primary Carer', '88992233', 'Supports daily glucose monitoring'),
(4, 'Farah Rahman', 'Mother / Legal Guardian', '93453453', 'Required for consent and follow-ups'),
(5, 'Linda Wong', 'Mother', '93334444', 'Handles clinic visits and medication pickups');

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
