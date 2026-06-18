def estimate_wait_time(priority):

    wait_map = {
        "Critical": "Immediate",
        "High": "10 Minutes",
        "Medium": "20 Minutes",
        "Low": "30 Minutes"
    }

    return wait_map.get(
        priority,
        "30 Minutes"
    )


def queue_position(priority):

    positions = {
        "Critical": 1,
        "High": 3,
        "Medium": 5,
        "Low": 8
    }

    return positions.get(
        priority,
        8
    )


def priority_color(priority):

    colors = {
        "Critical": "danger",
        "High": "warning",
        "Medium": "info",
        "Low": "success"
    }

    return colors.get(
        priority,
        "secondary"
    )


def queue_recommendation(priority):

    recommendations = {
        "Critical": "Immediate consultation required.",
        "High": "Patient should be attended within 10 minutes.",
        "Medium": "Patient can wait in standard queue.",
        "Low": "Routine consultation recommended."
    }

    return recommendations.get(
        priority,
        "Routine consultation recommended."
    )


def calculate_department_load(
    total_patients,
    doctors_available
):

    if doctors_available == 0:
        return 100

    load = (
        total_patients /
        doctors_available
    ) * 10

    return min(
        round(load, 2),
        100
    )


def resource_suggestion(load):

    if load >= 90:

        return (
            "Critical Load. "
            "Assign additional doctors immediately."
        )

    if load >= 70:

        return (
            "High Load. "
            "Consider reallocating staff."
        )

    if load >= 50:

        return (
            "Moderate Load. "
            "Monitor queue regularly."
        )

    return (
        "Department operating normally."
    )