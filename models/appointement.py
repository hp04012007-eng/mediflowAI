class Appointment:

    def __init__(
        self,
        id,
        patient_id,
        doctor_id,
        appointment_date,
        status
    ):

        self.id = id
        self.patient_id = patient_id
        self.doctor_id = doctor_id
        self.appointment_date = appointment_date
        self.status = status