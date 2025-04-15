import random
from datetime import datetime, date, time, timedelta

class SplunkApi:
    def get_logs(self, app_name: str, days: int) -> list[dict[str, any]]:
        """
        Mock method to simulate fetching logs from Datadog API.
        Returns a list of log entries as dictionaries.
        """
        mock_logs = MockSplunkLogGenerator()
        return mock_logs.get_logs_for_app(app_name, days)

class MockSplunkLogGenerator:
    """
    A class to generate mock Splunk log entries for multiple applications and hosts over a 30-day period.
    Logs are stored in a list of dictionaries, each containing a timestamp, log level, application name, host name, and message.
    The class can return logs for a specified application and a given number of recent days.
    """
    def __init__(self):
        # Define the applications and hosts for which to generate logs
        self.applications = ['AuthService', 'PaymentService', 'InventoryService', 'UserService']
        self.hosts = ['host1', 'host2']
        
        # Define sample log messages for each application and log level, ensuring realistic examples and variety
        self.log_messages = {
            'AuthService': {
                'info': [
                    "User {id} successfully logged in.",
                    "Token issued for user {id}.",
                    "Session terminated for user {id}."
                ],
                'warning': [
                    "Failed login attempt for user {id}.",
                    "Token for user {id} expiring soon.",
                    "Unexpected logout for user {id}."
                ],
                'error': [
                    "Database connection error.",
                    "Authentication server not reachable.",
                    "Unhandled exception in authentication module."
                ]
            },
            'PaymentService': {
                'info': [
                    "Payment processed for order {id}.",
                    "Invoice {id} sent to customer.",
                    "Refund issued for order {id}."
                ],
                'warning': [
                    "Payment processing delay for order {id}.",
                    "Retrying payment for order {id} due to network issue.",
                    "High latency in payment gateway."
                ],
                'error': [
                    "Payment failed for order {id}: insufficient funds.",
                    "Payment gateway error for order {id}.",
                    "Transaction error: currency mismatch for order {id}."
                ]
            },
            'InventoryService': {
                'info': [
                    "Stock check complete for item {id}. Quantity: {qty}.",
                    "New item {id} added to inventory.",
                    "Inventory report generated."
                ],
                'warning': [
                    "Low stock warning for item {id}.",
                    "Inventory sync delay detected.",
                    "Item {id} reserved stock discrepancy."
                ],
                'error': [
                    "Failed to update inventory for item {id}.",
                    "Inventory database timeout.",
                    "Inventory service error: invalid item ID."
                ]
            },
            'UserService': {
                'info': [
                    "User profile updated for user {id}.",
                    "New user registration: user {id}.",
                    "Password changed for user {id}."
                ],
                'warning': [
                    "User {id} profile update incomplete.",
                    "Password attempt limit nearing for user {id}.",
                    "Inactive account login attempt for user {id}."
                ],
                'error': [
                    "User database connection failure.",
                    "Data consistency error for user {id}.",
                    "Unhandled exception in user service."
                ]
            }
        }
        
        # Generate the logs dataset for the last 30 days (with logs present on 20 random days)
        self.logs = self._generate_logs()
    
    def _generate_logs(self):
        """
        Internal method to generate mock log entries for all applications and hosts over a 30-day period.
        Returns:
            List[dict]: A list of log entries (each entry is a dictionary).
        """
        logs_list = []  # List to accumulate log entries
        
        # Determine the date range: from 29 days ago up to today (30 days total)
        end_date = date.today()
        start_date = end_date - timedelta(days=29)
        
        # Create a list of all dates in the range
        all_dates = [(start_date + timedelta(days=i)) for i in range(30)]
        # Randomly select 20 dates out of the 30 to have logs (10 days will have no logs)
        log_dates = sorted(random.sample(all_dates, 20))
        
        # Use random generation for times and log levels, so each run yields different log entries
        for log_date in log_dates:
            # For each selected date, generate logs for each application
            for app in self.applications:
                # Generate 10 random timestamps for this date (ensuring chronological order within the day)
                times = []
                for _ in range(10):
                    hour = random.randint(0, 23)
                    minute = random.randint(0, 59)
                    second = random.randint(0, 59)
                    dt = datetime.combine(log_date, time(hour, minute, second))  # combine date with time
                    times.append(dt)
                times.sort()  # sort timestamps so logs are in time order
                
                # Determine log levels for the 10 entries (mix of error, warning, info; more infos for realism)
                levels = ['info'] * 5 + ['warning'] * 3 + ['error'] * 2
                random.shuffle(levels)  # shuffle the list to mix log levels in chronological sequence
                
                # Create 10 log entries for this application on this date
                for idx in range(10):
                    level = levels[idx]
                    timestamp = times[idx].strftime("%Y-%m-%dT%H:%M:%SZ")  # Format timestamp in ISO 8601 (UTC 'Z' notation)
                    host = random.choice(self.hosts)
                    # Pick a random message template for the given application and level
                    message_template = random.choice(self.log_messages[app][level])
                    random_qty = None
                    random_id=None
                    # Populate dynamic fields in the message template if present (e.g., {id}, {qty})
                    if '{id}' in message_template:
                        random_id = random.randint(100, 999)  # random ID (user ID, order ID, item ID, etc.)
                    if '{qty}' in message_template:
                        random_qty = random.randint(1, 100)   # random quantity for inventory messages
                    try:
                        # Attempt to format the message with both 'id' and 'qty' (extra keys are ignored if not needed)
                        message = message_template.format(id=random_id, qty=random_qty)
                    except KeyError:
                        # If some placeholder was not needed in the template, format with only the required ones
                        if '{id}' in message_template:
                            message = message_template.format(id=random_id)
                        elif '{qty}' in message_template:
                            message = message_template.format(qty=random_qty)
                        else:
                            message = message_template
                    
                    # Append the log entry (as a dictionary) to the list
                    logs_list.append({
                        "timestamp": timestamp,
                        "level": level,
                        "application": app,
                        "host": host,
                        "message": message
                    })
        return logs_list
    
    def get_logs_for_app(self, app_name, days):
        """
        Retrieve log entries for a specific application within the given number of days from today.
        Args:
            app_name (str): The name of the application to filter logs for.
            days (int): The number of days from the current date to include (e.g., 7 for the last week).
        Returns:
            List[dict]: A list of log entries for the specified application and time range.
        """
        # Ensure the 'days' parameter is within valid range (1 to 30 days)
        if days < 1:
            return []
        if days > 30:
            days = 30
        
        # Calculate date range for filtering: from (today - days + 1) to today
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        # Filter logs by application name and timestamp within the date range
        filtered_logs = []
        for entry in self.logs:
            if entry['application'] == app_name:
                #print(f"Entry application: {entry['application']}, Entry date: {entry['timestamp'][:10]}")
                entry_date_str = entry['timestamp'][:10]
                try:
                    entry_date = datetime.strptime(entry_date_str, "%Y-%m-%d").date()
                except ValueError:
                    continue  # skip entry if timestamp format is unexpected
                # Include log entry if its date falls within the specified range
                if start_date <= entry_date <= end_date:
                    filtered_logs.append(entry)
        return filtered_logs

# Example usage:
# generator = MockSplunkLogGenerator()
# logs = generator.get_logs_for_app("AuthService", 7)  # get logs for AuthService from the last 7 days
# print(logs)  # This will print a list of log entries (dictionaries) for that application and time range
