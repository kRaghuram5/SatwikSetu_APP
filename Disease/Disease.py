from ingestion import Event


class DiseaseService:
    def __init__(self):
        pass

    def create_disease_notification(self, event: Event):
        if event.isDisease:
            print(f"Notification: Health is BAD - Disease detected for prediction {event.prediction_id}", flush=True)
        else:
            print(f"Notification: Health is GOOD - No disease detected for prediction {event.prediction_id}", flush=True)

