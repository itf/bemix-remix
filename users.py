from database import db

class User:
    def __init__(self, request):
        #self.user = db.users.get_or_create(ip=request.META['REMOTE_ADDR'])
        self.type = "ip"
        self.ip = request.META['REMOTE_ADDR']
        '''else:
            self.user = db.users.find_one({'email': request.certificate_email})
            if self.user != None:
                self.type = "email"
                self.full_email = request.certificate_email
                (self.email, self.domain) = self.full_email.split('@')'''
        self.preferences = []
    def pref_true(self, pref):
        if not pref in self.preferences:
            return False
        return self.preferences[pref]
    def pref_value(self, pref):
        if not pref in self.preferences:
            return 0
        return self.preferences[pref]
    def save_preferences(self):
        self.user['preferences'] = self.preferences
        #db.users.save(self.user)
