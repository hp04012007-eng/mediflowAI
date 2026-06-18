def classify_urgency(symptoms):

    symptoms = symptoms.lower()

    critical_keywords = [
        "chest pain",
        "heart attack",
        "stroke",
        "unconscious",
        "breathing difficulty",
        "shortness of breath",
        "severe bleeding"
    ]

    high_keywords = [
        "high fever",
        "severe pain",
        "fracture",
        "infection",
        "vomiting blood"
    ]

    medium_keywords = [
        "headache",
        "stomach pain",
        "dizziness",
        "cough",
        "fatigue"
    ]

    for keyword in critical_keywords:
        if keyword in symptoms:
            return "Critical"

    for keyword in high_keywords:
        if keyword in symptoms:
            return "High"

    for keyword in medium_keywords:
        if keyword in symptoms:
            return "Medium"

    return "Low"


def assign_department(symptoms):

    symptoms = symptoms.lower()

    cardiology = [
        "chest pain",
        "heart",
        "blood pressure",
        "palpitations"
    ]

    neurology = [
        "stroke",
        "headache",
        "seizure",
        "migraine",
        "dizziness"
    ]

    orthopedics = [
        "fracture",
        "bone",
        "joint",
        "ankle",
        "knee"
    ]

    pulmonology = [
        "breathing",
        "lung",
        "asthma",
        "shortness of breath"
    ]

    for word in cardiology:
        if word in symptoms:
            return "Cardiology"

    for word in neurology:
        if word in symptoms:
            return "Neurology"

    for word in orthopedics:
        if word in symptoms:
            return "Orthopedics"

    for word in pulmonology:
        if word in symptoms:
            return "Pulmonology"

    return "General Medicine"


def calculate_priority_score(urgency):

    scores = {
        "Critical": 95,
        "High": 80,
        "Medium": 60,
        "Low": 30
    }

    return scores.get(
        urgency,
        30
    )


def estimate_wait_time(urgency):

    wait_times = {
        "Critical": "Immediate",
        "High": "10 Minutes",
        "Medium": "20 Minutes",
        "Low": "30 Minutes"
    }

    return wait_times.get(
        urgency,
        "30 Minutes"
    )