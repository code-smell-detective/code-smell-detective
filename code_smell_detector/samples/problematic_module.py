"""Sample module containing intentional code smells for testing."""


class OrderProcessor:
    def process_order(self, order, payment_service, inventory_service, notification_service, audit_service):
        total = 0
        for item in order.items:
            total += item.price * item.quantity
        if order.customer.is_vip:
            total = total * 0.9

        if order.country == "US":
            if order.state == "CA":
                tax = total * 0.075
            elif order.state == "NY":
                tax = total * 0.085
            elif order.state == "TX":
                tax = total * 0.065
            else:
                tax = total * 0.05
        elif order.country == "NL":
            tax = total * 0.21
        else:
            tax = total * 0.15

        total += tax

        payment_service.charge(order.customer, total)
        inventory_service.reserve(order.items)
        notification_service.email(order.customer.email, "Order processed")
        audit_service.log("processed order", order.id, total)

        if total > 1000:
            notification_service.sms(order.customer.phone, "High value order processed")
            audit_service.log("high value order", order.id, total)

        return total


class SystemManager:
    def __init__(self):
        self.logger = None
        self.config = {}
        self.metrics = {}
        self.alerts = []
        self.sessions = []
        self.security_events = []

    def configure_logging(self):
        self.logger = "configured"

    def configure_metrics(self):
        self.metrics = {"enabled": True}

    def configure_alerts(self):
        self.alerts.append("configured")

    def configure_sessions(self):
        self.sessions.append("configured")

    def configure_security(self):
        self.security_events.append("configured")

    def start_services(self):
        self.configure_logging()
        self.configure_metrics()
        self.configure_alerts()
        self.configure_sessions()
        self.configure_security()

    def stop_services(self):
        self.logger = None
        self.metrics = {}
        self.alerts.clear()
        self.sessions.clear()
        self.security_events.clear()

    def restart(self):
        self.stop_services()
        self.start_services()

    def audit(self):
        return {
            "logger": self.logger,
            "metrics": self.metrics,
            "alerts": len(self.alerts),
            "sessions": len(self.sessions),
            "security_events": len(self.security_events),
        }

    def monitor_database(self):
        return True

    def monitor_queue(self):
        return True

    def monitor_cache(self):
        return True

    def rotate_logs(self):
        return True

    def backup_database(self):
        return True

    def backup_cache(self):
        return True

    def backup_sessions(self):
        return True

    def backup_security_events(self):
        return True

    def update_config(self, key, value):
        self.config[key] = value

    def remove_config(self, key):
        self.config.pop(key, None)

    def list_services(self):
        return ["logging", "metrics", "alerts", "sessions", "security"]

    def service_status(self, name):
        return True

    def reset_metrics(self):
        self.metrics = {}

    def reset_alerts(self):
        self.alerts = []

    def reset_sessions(self):
        self.sessions = []

    def reset_security_events(self):
        self.security_events = []

    def sync_remote(self):
        return True

    def validate_configuration(self):
        return bool(self.config)

    def apply_policies(self):
        return True

    def enforce_security(self):
        return True


def duplicate_logic(a, b):
    # duplicated block 1
    result = []
    for item in a:
        if item > 10:
            result.append(item * 2)
    return result


def duplicate_logic_variant(a, b):
    # duplicated block 2
    result = []
    for item in a:
        if item > 10:
            result.append(item * 2)
    return result

