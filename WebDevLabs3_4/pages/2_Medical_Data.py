# Lab 3: API data page
# TODO: Rename this file to fit your page. Keep the number at the front, since it sets the
#       page's order in the sidebar (for example, 2_Pokedex.py).
#
# This page shows data from your API, processed with your own Python code. No AI on this page.
# It should have:
#   - at least 2 meaningful user inputs (for example st.selectbox, st.text_input, st.slider)
#   - at least 2 dynamic visuals that change based on the user's input: charts, displays of
#     images, or other visualizations (see the example website for examples!)

import os

import requests
import streamlit as st
disease_types = {
    "Respiratory": {
        "letter": "J",
        "image": "respiratory",
        "doctor": "Pulmonologist",
    },
    "Heart & Blood Vessels": {
        "letter": "I",
        "image": "heart_blood_vessels",
        "doctor": "Cardiologist",
    },
    "Digestive": {
        "letter": "K",
        "image": "digestive",
        "doctor": "Gastroenterologist",
    },
    "Nervous System": {
        "letter": "G",
        "image": "nervous_system",
        "doctor": "Neurologist",
    },
    "Skin": {
        "letter": "L",
        "image": "skin",
        "doctor": "Dermatologist",
    },
    "Bones & Muscles": {
        "letter": "M",
        "image": "bones_muscles",
        "doctor": "Orthopedist",
    },
}

symptom_words = {
    "Cough": "cough",
    "Fever": "fever",
    "Fatigue": "fatigue",
    "Wheezing": "wheez",
    "Shortness of breath": "breath",
    "Chest pain": "chest pain",
    "Headache": "headache",
    "Dizziness": "dizz",
    "Numbness": "numb",
    "Weakness": "weak",
    "Confusion": "confus",
    "Seizures": "seizure",
    "Vision problems": "vision",
    "Nausea": "nausea",
    "Vomiting": "vomit",
    "Diarrhea": "diarrhea",
    "Constipation": "constipat",
    "Bloating": "bloat",
    "Loss of appetite": "appetite",
    "Weight loss": "weight loss",
    "Swelling": "swell",
    "Rash": "rash",
    "Itching": "itch",
    "Redness": "redness",
    "Joint pain": "joint pain",
    "Stiffness": "stiff",
    "Sweating": "sweat",
    "Chills": "chill",
    "Sore throat": "sore throat",
    "Irregular heartbeat": "heartbeat",
}
organ_words = {
    "Lungs": "lung",
    "Nose": "nose",
    "Throat": "throat",
    "Airways": "airway",
    "Heart": "heart",
    "Arteries": "arter",
    "Veins": "vein",
    "Stomach": "stomach",
    "Intestines": "intestin",
    "Liver": "liver",
    "Esophagus": "esophag",
    "Brain": "brain",
    "Spinal cord": "spinal cord",
    "Nerves": "nerve",
    "Skin": "skin",
    "Hair": "hair",
    "Nails": "nail",
    "Bones": "bone",
    "Muscles": "muscle",
    "Joints": "joint",
}

#SECTION 2: GET AND PROCESS DATA
@st.cache_data
def get_conditions(letter):
    url = "https://clinicaltables.nlm.nih.gov/api/conditions/v3/search?terms=*&q=icd10cm_codes:" + letter + "*&df=consumer_name&ef=icd10cm_codes&maxList=500"
    response = requests.get(url)
    data = response.json()

    codes = data[2]["icd10cm_codes"]
    names = data[3]

    conditions = {}
    for i in range(len(names)):
        name = names[i][0]
        code = codes[i].split(",")[0]
        if code.startswith(letter):
            conditions[name] = code
    return conditions 

@st.cache_data
def get_entry(code):
    url = "https://connect.medlineplus.gov/service?mainSearchCriteria.v.cs=2.16.840.1.113883.6.90&mainSearchCriteria.v.c=" + code + "&knowledgeResponseType=application/json"
    response = requests.get(url)
    if response.status_code != 200:
        return {}
    data = response.json()

    if "entry" not in data["feed"] or len(data["feed"]["entry"]) == 0:
        return {}
    return data["feed"]["entry"][0]

def get_summary(code):
    entry = get_entry(code)
    if entry == {}:
        return ""
    return entry["summary"]["_value"]



def get_section(summary, keywords):
    pieces = summary.split("<h3>")
    for piece in pieces:
        parts = piece.split("</h3>")
        if len(parts) == 2:
            heading = parts[0].lower()
            for keyword in keywords:
                if keyword in heading:
                    return parts[1]
            
    return ""
def get_about(summary):
    if "<h3>" not in summary:
        return summary
    pieces = summary.split("<h3>")
    return pieces[1].split("</h3>")[1]

@st.cache_data
def get_details(code):
    summary = get_summary(code)
    details = {
        "about": get_about(summary),
        "symptoms": get_section(summary, ["symptom", "signs", "problems can"]),
        "causes": get_section(summary, ["what causes", "causes of", "cause of"]),
        "prevention": get_section(summary, ["prevent"]),
    }
    return details
def find_organs(details):
    text = (details["about"] + details["symptoms"] + details["causes"] + details["prevention"]).lower()
    found = []
    for organ in organ_words:
        if organ_words[organ] in text:
            found.append(organ)
    return found

def get_sample(letter):
    conditions = get_conditions(letter)
    sample = {}
    seen = []
    checked = 0
    for name in conditions:
        if checked == 25:
            break
        checked = checked + 1 
        details = get_details(conditions[name])
        if details["about"] != "" and details["about"] not in seen:
            sample[name] = details
            seen.append(details["about"])
    return sample

@st.cache_data  
def count_symptoms(letter):
    sample = get_sample(letter)
    counts = {}
    for name in sample:
        text = sample[name]["symptoms"].lower() + sample[name]["about"].lower()
        for symptom in symptom_words:
            if symptom_words[symptom] in text:
                if symptom in counts:
                    counts[symptom] = counts[symptom] + 1
                else:
                    counts[symptom] = 1
    return counts
def find_by_symptom(symptom, letter):
    sample = get_sample(letter)
    matches = []
    for name in sample:
        text = (sample[name]["symptoms"].lower() + sample[name]["about"].lower())
        if symptom.lower() in text:
            matches.append(name)
    return matches

def image_path(name):
    base = "images/" + name.lower().replace(" ", "_")
    for ending in [".png", ".jpg", ".jpeg"]:
        if os.path.exists(base + ending):
            return base + ending
    return base + ".png"  # Default to .png if no file exists

#SECTION 3: USER INPUTS
st.title("Disease Finder")

with st.expander("Number of Diseases/Conditions Per Type", expanded=True):
    all_types = list(disease_types.keys())
    chosen_types = st.multiselect("Choose disease and conditions types to display", all_types, default=all_types[:4])

    type_names = []
    counts = []
    for type_name in chosen_types:
        letter = disease_types[type_name]["letter"]
        type_names.append(type_name)
        counts.append(len(get_conditions(letter)))
    char_data = {"Type": type_names, "Number of Diseases/Conditions": counts}
    st.bar_chart(char_data, x= "Type", y= "Number of Diseases/Conditions") 
    st.caption("This chart changes with the selected condition types") 
    
 #SECTION 4: PICK A TYPE (USER INPUT #2, DYNAMIC #2))
st.write("Search for a disease by type to learn about it!")

selected_type = st.selectbox("Choose a condition type", all_types, index=None, placeholder= "Select a body system...")
if selected_type is None:
    st.stop()
type_info = disease_types[selected_type]


col1, col2 = st.columns(2)
with col1:
    st.image(image_path(type_info["image"]), width =300)
with col2:
    st.subheader("Doctor to See")
    st.image(image_path(type_info["doctor"]), width=200, caption=type_info["doctor"])
st.header("Most Common Symptoms")
with st.spinner("Reading MedlinePlus summaries..."):
    symptom_counts = count_symptoms(type_info["letter"])
if len(symptom_counts) == 0:
    st.warning("MedlinePlus does not have information on this condition type.")
else:
    symptom_chart = {"Symptom": list(symptom_counts.keys()), "Number of Conditions": list(symptom_counts.values())}
    st.bar_chart(symptom_chart, x= "Symptom", y= "Number of Conditions")
    st.caption("This chart changes with the selected condition type")



#SECTION 5: PICK A CONDITION (USER INPUT #3)
conditions = get_conditions(type_info["letter"])
condition_names = sorted(conditions.keys())

selected_condition = st.selectbox("Choose a disease or condition", condition_names, index= None, placeholder="Select a condition or disease")
if selected_condition is None:
    st.stop()
code = conditions[selected_condition]
summary = get_summary(code)

if summary == "":
    st.warning("MedlinePlus does not have information on this condition.")
else:
    details = get_details(code)
    st.subheader(selected_condition)
    st.markdown(details["about"], unsafe_allow_html=True)

    st.subheader("Organs Affected")
    organs = find_organs(details)
    if len(organs) == 0:
        st.write("No specific organs are mentioned in the MedlinePlus summary for this condition.")
    else:
        organ_cols = st.columns(len(organs))
        for i in range(len(organs)):
            with organ_cols[i]:
                st.image(image_path(organs[i]), width=60, caption=organs[i])


    col3, col4, col5 = st.columns(3)
    with col3:
        if details["symptoms"] != "":
            st.header("Symptoms")
            with st.expander("What are the symptoms?"):
                st.markdown(details["symptoms"], unsafe_allow_html=True)

    with col4:
        if details["causes"] != "":
            st.subheader("Causes")
            with st.expander("What causes this this?"):
                st.markdown(details["causes"], unsafe_allow_html=True)
    with col5:
        if details["prevention"] != "":
            st.header("Prevention")
            with st.expander("Can it be prevented?"):
                st.markdown(details["prevention"], unsafe_allow_html=True)

    st.caption("ICD-10 code: " + code + " | Source: MedlinePlus (U.S. National Library of Medicine)")
#Section 6
st.header ("symptom search")
symptom = st.text_input("Type in a symptom to search for " + selected_type + " conditions")

if symptom != "":
    matches = find_by_symptom(symptom, type_info["letter"])
    if len(matches) == 0:
        st.write("No conditions found with that symptom. Try a shorter word. Like cough instead of coughing.")
    else:
        st.write("Conditions that list **" + symptom + "** as a symptom:")
        for match in matches:
            st.markdown(":blue-background[" + match + "]")

    st.caption("This tool is for learning and reference only. Always seek the advice of a qualified health provider.")