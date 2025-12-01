import streamlit as st
import requests
from auth_utils import hydrate_auth_from_params
from config import PATIENTS_API

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
            response = requests.get(f"{PATIENTS_API}/{patient_id}", timeout=5)
            if response.status_code != 200:
                st.error(response.json().get("detail", "Error fetching patient"))
            else:
                data = response.json()

                patient = data["patient"]
                conditions = data["conditions"]
                appointments = data["appointments"]
                referrals = data["referrals"]
                carers = data.get("carers", [])
                medications = data.get("medications", [])
                age = patient.get("age")
                age_group = patient.get("age_group")
                requires_carer = patient.get("requires_carer")

                # Patient Info
                with st.expander("👤 Basic Information", expanded=True):
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
                with st.expander("🧑‍🤝‍🧑 Carer / Guardian", expanded=False):
                    if len(carers) == 0:
                        if requires_carer:
                            st.error("No carer/guardian on file for this patient.")
                        else:
                            st.info("No carer or guardian recorded.")
                    else:
                        for c in carers:
                            st.markdown(f"**{c['full_name']}** — {c['relationship_to_patient']}")
                            st.write(f"Contact: {c['contact_number']}")
                            if c.get("notes"):
                                st.caption(f"Notes: {c['notes']}")
                            st.divider()

                # Conditions
                with st.expander("🩺 Medical Conditions", expanded=False):
                    if len(conditions) == 0:
                        st.info("No medical conditions recorded.")
                    else:
                        for c in conditions:
                            st.write(f"- **{c['condition_name']}** ({c['severity_level']}) diagnosed on {c['diagnosed_date']}")

                # Appointments
                with st.expander("📅 Appointments", expanded=False):
                    if len(appointments) == 0:
                        st.info("No appointment history.")
                    else:
                        for a in appointments:
                            st.markdown(f"**Appointment #{a['appointment_id']}**")
                            st.write(f"Doctor: {a['doctor']} ({a['specialization']})")
                            st.write(f"Date: {a['date']}")
                            st.write(f"Status: {a['status']}")
                            st.divider()

                # Referrals
                with st.expander("📝 Referrals", expanded=False):
                    if len(referrals) == 0:
                        st.info("No referrals found.")
                    else:
                        for r in referrals:
                            st.write(f"- Referred to **{r['referred_to_specialization']}** → Status: {r['status']}")
                            st.caption(f"Reason: {r['reason']}")

                # Medication Schedules
                with st.expander("💊 Medication Schedule", expanded=True):
                    if len(medications) == 0:
                        st.info("No medication schedules found.")
                    else:
                        table_rows = []
                        for m in medications:
                            status = m.get("status", "pending")
                            status_display = {
                                "taken": "✅ TAKEN",
                                "pending": "🟠 PENDING",
                                "missed": "🔴 MISSED",
                            }.get(status, status.upper())
                            table_rows.append({
                                "Medication": m.get("medication_name", ""),
                                "Dosage": m.get("dosage", ""),
                                "Frequency": m.get("frequency", ""),
                                "Time": m.get("intake_time", ""),
                                "Start": m.get("start_date", ""),
                                "End": m.get("end_date", ""),
                                "Status": status_display,
                                "Remarks": m.get("remarks", ""),
                            })
                        st.dataframe(table_rows, hide_index=True, use_container_width=True)

        except Exception as e:
            st.error(str(e))
