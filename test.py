def fetch_data():
    pass

def process_data():
    fetch_data()
    print("Data processed")

class Manager:
    def execute(self):
        process_data()
        self.log_event()

    def log_event(self):
        pass
