class Patient:

    def __init__(
        self,
        id,
        user_id,
        age,
        gender,
        symptoms,
        priority,
        department,
        status
    ):

        self.id = id
        self.user_id = user_id
        self.age = age
        self.gender = gender
        self.symptoms = symptoms
        self.priority = priority
        self.department = department
        self.status = status