"""Sample codebase demonstrating Phase 1 code smells for the detector."""


def process_invoice(order, payment_service, inventory_service, notification_service, audit_service, discount_service):
    """Intentionally long, complex method for analysis."""
    total = 0
    for line in order.lines:
        total += line.price * line.quantity

    if order.customer.is_vip:
        total -= discount_service.calculate_vip_discount(order)

    for adjustment in order.adjustments:
        if adjustment.type == "PROMO":
            total -= adjustment.value
        elif adjustment.type == "FEE":
            total += adjustment.value

    if order.country == "US":
        if order.state == "CA":
            tax_rate = 0.095
        elif order.state == "NY":
            tax_rate = 0.085
        elif order.state == "TX":
            tax_rate = 0.072
        else:
            tax_rate = 0.065
    elif order.country == "DE":
        tax_rate = 0.19
    elif order.country == "NL":
        tax_rate = 0.21
    elif order.country == "UK":
        if order.region == "Scotland":
            tax_rate = 0.2
        elif order.region == "Northern Ireland":
            tax_rate = 0.19
        else:
            tax_rate = 0.21
    else:
        tax_rate = 0.17

    total += total * tax_rate

    payment_service.charge(order.customer, total)
    inventory_service.reserve(order.lines)
    notification_service.email(order.customer.email, f"Invoice processed for {total}")
    audit_service.record("INVOICE_PROCESSED", order.id, total)

    if total > 5000:
        notification_service.sms(order.customer.phone, "High value invoice processed")
        audit_service.record("HIGH_VALUE_INVOICE", order.id, total)

    return total


def duplicate_block_one(items):
    result = []
    for item in items:
        if item.status == "active":
            result.append(item.value * 2)
    return result


def duplicate_block_two(items):
    result = []
    for item in items:
        if item.status == "active":
            result.append(item.value * 2)
    return result


class MegaManager:
    """Large class with too many responsibilities."""

    def setup_logging(self):
        return "logging"

    def setup_metrics(self):
        return "metrics"

    def setup_alerts(self):
        return "alerts"

    def setup_cache(self):
        return "cache"

    def setup_sessions(self):
        return "sessions"

    def setup_security(self):
        return "security"

    def setup_database(self):
        return "database"

    def setup_search(self):
        return "search"

    def setup_payments(self):
        return "payments"

    def setup_notifications(self):
        return "notifications"

    def setup_integration_a(self):
        return "integration_a"

    def setup_integration_b(self):
        return "integration_b"

    def setup_integration_c(self):
        return "integration_c"

    def setup_integration_d(self):
        return "integration_d"

    def setup_integration_e(self):
        return "integration_e"

    def setup_integration_f(self):
        return "integration_f"

    def setup_integration_g(self):
        return "integration_g"

    def setup_integration_h(self):
        return "integration_h"

    def setup_integration_i(self):
        return "integration_i"

    def setup_integration_j(self):
        return "integration_j"

    def setup_integration_k(self):
        return "integration_k"


