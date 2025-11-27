# MyAIHealthLine
**Smart, accessible healthcare — right in your hands.**

MyAIHealthLine is an AI-powered, multi-agent healthcare support system designed to help underserved communities where long clinic queues, limited medical staff, and frequent power interruptions make access to care difficult.  
The system brings healthcare to the palm of your hand through mobile, SMS, and low-resource–friendly technologies.

---

## 🚀 Project Overview

MyAIHealthLine uses a cooperative multi-agent setup to:
- Register patients and caregivers  
- Provide symptom-based triage  
- Assign queue numbers remotely  
- Manage clinic appointments and referrals  
- Assist doctors with records and consultation notes  
- Deliver SMS and in-app notifications  
- Handle medicine reminders and scheduling  
- Remain resilient during power outages  

Designed for local deployment using Docker and minimal hardware, it's ideal for rural clinics, small municipalities, NGOs, or community health centers.

---

## 🧠 Core Agent System

### **1. Concierge Agent**
- Registers new patients and guardians  
- Collects symptoms  
- Performs emergency triage  
- Issues queue numbers  

### **2. Database Agent**
- Stores and retrieves patient data  
- Syncs data reliably after outages  

### **3. Scheduler Agent**
- Manages queue order  
- Schedules appointments  
- Estimates wait times  

### **4. Notification Agent**
- Sends SMS, email, and app notifications  
- Handles medicine reminders  
- Works during power interruptions  

### **5. Doctor Assistant Agent**
- Provides access to patient history  
- Records consultation notes  
- Issues prescriptions  

### **6. Specialist Referral Agent**
- Creates referral documents  
- Sends follow-up notifications  

### **7. Medicine Scheduler Agent**
- Generates medicine intake reminders  
- Tracks medication routines  
- Allows patient–doctor change requests  

---

## 📦 Tech Stack

- **Backend:** FastAPI  
- **Agent Framework:** Custom Python agent orchestrator  
- **Database:** PostgreSQL (or SQLite for lightweight demo)  
- **Queueing & Scheduling:** Internal agents  
- **Notifications:** SMS (via Mock API for demo), Email, App  
- **Deployment:** Docker Compose  
- **Monitoring:** Basic observability through logs + agent events  

---
## Folder Structure

```
myaihealthline/
│
├── api/
│   ├── app/
│   │   ├── main.py
│   │   ├── db.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── agents/
│   │   │   ├── base.py
│   │   │   ├── concierge_agent.py
│   │   │   ├── db_agent.py
│   │   │   ├── scheduler_agent.py
│   │   │   ├── notification_agent.py
│   │   │   ├── doctor_assistant_agent.py
│   │   │   ├── referral_agent.py
│   │   │   └── medicine_scheduler_agent.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── infra/
│   ├── docker-compose.yml
│   └── nginx/
│
├── docs/
│   ├── architecture_diagram.svg
│   ├── erd.png
│   ├── folder_structure.md
│   └── landing_page.md
│
├── tests/
│
└── README.md
```


---

## 🏗️ Architecture Diagram (Text)

```
Patient / Guardian (App or SMS)
            |
            v
      Concierge Agent
            |
            v
  +-----------------------+
  |     Agent Hub         |
  | (Orchestrator Layer)  |
  +-----------------------+
   |        |         |        
   v        v         v
DB Agent   Scheduler   Notification
   |                        |
   v                        v
Database  <-->  Doctor Assistant Agent  <-->  Referral Agent
                                  |
                                  v
                        Medicine Scheduler Agent
```

---

## 🗄️ Database Schema (Simplified)

Key tables:
- **patients**
- **guardians**
- **appointments**
- **visits**
- **prescriptions**
- **medication_schedules**
- **reminders**
- **referrals**
- **doctors**
- **users**

(See docs/ for full ERD.)

---

## 🐳 Deployment (Docker Compose)

1. Clone the repository:
```bash
git clone https://github.com/yourname/myaihealthline
cd myaihealthline
```

2. Run with Docker Compose:
```bash
docker compose up -d
```

3. Access API:
```
http://localhost:8000/docs
```

---

## 📱 Features for Low-Resource Communities

- Offline-friendly workflows  
- SMS fallback for reminders and queue updates  
- Mobile-friendly doctor and admin UI  
- Automatic resync after power restoration  
- Minimal data usage  

---

## 🎯 Target Users

- Rural clinics  
- Municipal health centers  
- NGOs / humanitarian groups  
- School clinics  
- Barangay health stations  

---

## 🧪 Future Enhancements

- Voice-based concierge agent  
- Multi-language SMS support  
- Offline-first PWA app  
- Analytics dashboard  
- Patient card QR scanning  

---

## 🤝 Contributing

Pull requests are welcome!  
This project aims to help communities in need — contributions that improve accessibility, reliability, and inclusivity are especially encouraged.

---

## 📜 License

MIT License  
Feel free to use, modify, and deploy for community benefit.

---

## 💙 Acknowledgements

Built as a capstone project for **Kaggle × Google AI Intensive Training (Agents for Good Track)**.  
Designed to empower communities through accessible, smart healthcare systems.

