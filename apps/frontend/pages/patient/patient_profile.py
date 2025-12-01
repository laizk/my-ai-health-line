import streamlit as st
import requests
from auth_utils import hydrate_auth_from_params

BACKEND_API = "http://backend:8010"

st.title("🧑‍⚕️ Patient Profile")

# Restore auth if the page is refreshed directly
hydrate_auth_from_params()
auth = st.session_state.get("auth")
if not auth:
    st.warning("Please login from the Login page to view patient records.")
    st.stop()

patients = auth.get("patients", [])
if len(patients) == 0:
    st.error("No patients linked to this account.")
    st.stop()

patient_map = {f"{p['full_name']} (ID {p['id']})": p["id"] for p in patients}
patient_label = st.selectbox("Select Patient", list(patient_map.keys()))
patient_id = patient_map[patient_label]

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
                carers = data.get("carers", [])
                age = patient.get("age")
                age_group = patient.get("age_group")
                requires_carer = patient.get("requires_carer")

                # Patient Info
                st.header("👤 Basic Information")
                st.write(f"**Name:** {patient['full_name']}")
                if age is not None:
                    group_label = age_group if age_group else "unknown group"
                    st.write(f"**Age:** {age} ({group_label})")
                st.write(f"**Birthdate:** {patient['birthdate']}")
                st.write(f"**Gender:** {patient['gender']}")
                st.write(f"**Contact:** {patient['contact_number']}")
                st.write(f"**Address:** {patient['address']}")
                st.write(f"**Emergency Contact:** {patient['emergency_contact']}")
                if requires_carer:
                    st.warning("This patient is a minor/elderly and should have an assigned carer or guardian.")

                # Carer / Guardian
                st.header("🧑‍🤝‍🧑 Carer / Guardian")
                if len(carers) == 0:
                    if requires_carer:
                        st.error("No carer/guardian on file for this patient.")
                    else:
                        st.info("No carer or guardian recorded.")
                else:
                    for c in carers:
                        st.subheader(c["full_name"])
                        st.write(f"**Relationship:** {c['relationship_to_patient']}")
                        st.write(f"**Contact:** {c['contact_number']}")
                        if c.get("notes"):
                            st.caption(f"Notes: {c['notes']}")

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
