import streamlit as st
import requests

BACKEND_API = "http://backend:8010"

st.title("🧑‍⚕️ Patient Profile")

# Search patient
patient_id = st.number_input("Enter Patient ID", min_value=1, step=1)

if st.button("Retrieve"):
    with st.spinner("Fetching patient data..."):
        try:
            response = requests.get(f"{BACKEND_API}/patients/{patient_id}", timeout=5)
            if response.status_code != 200:
                st.error(response.json().get("detail", "Error fetching patient"))
            else:
                data = response.json()

                patient = data["patient"]
                conditions = data["conditions"]
                appointments = data["appointments"]
                referrals = data["referrals"]

                # Patient Info
                st.header("👤 Basic Information")
                st.write(f"**Name:** {patient['full_name']}")
                st.write(f"**Birthdate:** {patient['birthdate']}")
                st.write(f"**Gender:** {patient['gender']}")
                st.write(f"**Contact:** {patient['contact_number']}")
                st.write(f"**Address:** {patient['address']}")
                st.write(f"**Emergency Contact:** {patient['emergency_contact']}")

                # Conditions
                st.header("🩺 Medical Conditions")
                if len(conditions) == 0:
                    st.info("No medical conditions recorded.")
                else:
                    for c in conditions:
                        st.write(f"- **{c['condition_name']}** ({c['severity_level']}) diagnosed on {c['diagnosed_date']}")

                # Appointments
                st.header("📅 Appointments")
                if len(appointments) == 0:
                    st.info("No appointment history.")
                else:
                    for a in appointments:
                        st.subheader(f"Appointment #{a['appointment_id']}")
                        st.write(f"**Doctor:** {a['doctor']} ({a['specialization']})")
                        st.write(f"**Date:** {a['date']}")
                        st.write(f"**Status:** {a['status']}")

                # Referrals
                st.header("📝 Referrals")
                if len(referrals) == 0:
                    st.info("No referrals found.")
                else:
                    for r in referrals:
                        st.write(f"- Referred to **{r['referred_to_specialization']}** → Status: {r['status']}")
                        st.caption(f"Reason: {r['reason']}")

        except Exception as e:
            st.error(str(e))
