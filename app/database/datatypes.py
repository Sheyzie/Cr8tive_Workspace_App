class Datatype:

    def __init__(self, *args, **kwargs):
        pass


class VarChar(Datatype):
    
    def __init__(self, *args, **kwargs):
        max_length = kwargs.get('max_length')
        super().__init__(*args, **kwargs)

    def __str__(self):
        return 
    
class Text(Datatype):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        
        return 'TEXT'
    

class Integer(Datatype):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return 'INTEGER'
    
class DateTime(Datatype):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __str__(self):
        return 'TEXT'