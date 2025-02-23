
class Student:

    def __init__(self, 
                student_icon: str, 
                school_icon: str, 
                damage_type: str,
                student_role: str, 
                ex_skill_cost: str, 
                weapon_type: str,
                student_height: str, 
                student_release_date: str):
        
        self._student_icon = student_icon
        self._school_icon = school_icon
        self._damage_type = damage_type
        self._student_role = student_role
        self._ex_skill_cost = ex_skill_cost
        self._weapon_type = weapon_type
        self._student_height = student_height
        self._student_release_date = student_release_date


    def get_student_icon(self) -> str:
        return self._student_icon
    
    def get_school_icon(self) -> str:
        return self._school_icon
    
    def get_damage_type(self) -> str:
        return self._damage_type
    
    def get_student_role(self) -> str:
        return self._student_role
    
    def get_ex_skill_cost(self) -> str:
        return self._ex_skill_cost
    
    def get_weapon_type(self) -> str:
        return self._weapon_type
    
    def get_student_height(self) -> str:
        return self._student_height
    
    def get_student_release_date(self) -> str:
        return self._student_release_date
    
    def __str__(self) -> str:
        return 