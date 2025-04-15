from datetime import datetime, timedelta
import random

class DatadogApi:
    def get_logs(self, app_name: str, days: int) -> list[dict[str, any]]:
        """
        Mock method to simulate fetching logs from Datadog API.
        Returns a list of log entries as dictionaries.
        """
        mock_logs = MockDatadogDataGenerator()
        return mock_logs.get_data(app_name, days)
    
class MockDatadogDataGenerator:
    def __init__(self, days=30, apps=None):
        """
        Initialize the mock data generator. Generates logs and events for given apps over the past `days` days.
        
        :param days: Number of days in the past to generate data for (default 30 days).
        :param apps: Dict of application names to application IDs (or list of app names). If None, uses default apps.
        """
        # Default applications and IDs if none provided
        if apps is None:
            # Use default app names with some mock IDs
            apps = {
                "frontend_app": "app-001",
                "backend_service": "app-002",
                "analytics_service": "app-003"
            }
        # If apps is provided as list of names, convert to dict with generated IDs
        elif isinstance(apps, list):
            apps = {name: f"app-{str(index+1).zfill(3)}" for index, name in enumerate(apps)}
        
        self.apps = apps
        self.days = days
        self.data = []  # will hold all log and event entries (as dicts)
        
        # Predefined hostnames per app for variety (2 hosts per app)
        self.app_hosts = {}
        for app in self.apps:
            # create two hostnames for each app
            base = app.replace(" ", "_").lower()
            self.app_hosts[app] = [f"{base}-host-1", f"{base}-host-2"]
        
        # Predefine some message templates for logs
        self.normal_info_messages = [
            "Successfully connected to database",
            "User login successful",
            "Background job executed",
            "Cache cleared",
            "Configuration reloaded",
            "Processed request to /api/endpoint",
        ]
        self.normal_warning_messages = [
            "High memory usage detected",
            "Disk space running low",
            "Response latency above threshold",
            "Using default configuration due to error",
            "Failed login attempt detected",
        ]
        self.normal_error_messages = [
            "Database connection lost",
            "NullPointerException in module X",
            "Unhandled exception occurred",
            "Out of memory error",
            "Failed to process user request",
            "Timeout while calling external API",
        ]
        # Metrics-related log message templates with placeholders.
        # Each template is paired with a list of keys for extra fields to add (excluding 'host' which is separate).
        self.metrics_info_templates = [
            ("Metrics Report: CPU: {cpu}%, Memory: {mem}MB, Pod Status: {status}, Ready: {ready}", 
             ["cpu", "memory", "pod_status", "ready"]),
            ("Node metrics - CPU usage: {cpu}%, Memory usage: {mem}MB", ["cpu", "memory"]),
        ]
        self.metrics_warning_templates = [
            ("High CPU usage: {cpu}% on host {host}", ["cpu"]),  # 'host' is already tracked separately
            ("Memory usage at {mem}MB exceeds safe limit", ["memory"]),
            ("Pod {pod} is in {status} state (not Running)", ["pod_name", "pod_status"]),
        ]
        self.metrics_error_templates = [
            ("Readiness probe failed for pod {pod}", ["pod_name"]),
            ("Pod {pod} status is {status} (crashed)", ["pod_name", "pod_status"]),
            ("OutOfMemory: {mem}MB used, exceeding limits", ["memory"]),
        ]
        
        # Generate the mock log and event data
        self._generate_data()
    
    def _generate_data(self):
        """Internal method to generate random logs and events data for all apps."""
        now = datetime.utcnow()
        # Generate data for each application
        for app, app_id in self.apps.items():
            hosts = self.app_hosts.get(app, ["localhost"])  # host options for this app
            
            # --- Generate log entries for this app ---
            num_logs = random.randint(50, 100)  # random number of logs for this app
            for _ in range(num_logs):
                # Random timestamp within the last `self.days` days
                offset_seconds = random.random() * (self.days * 24 * 3600)
                ts = now - timedelta(seconds=offset_seconds)
                # Format timestamp as ISO 8601 with milliseconds and Z (UTC)
                ts_str = ts.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
                
                host = random.choice(hosts)
                # Weighted random choice for log level (INFO most frequent)
                level = random.choice(["INFO"] * 3 + ["WARNING"] + ["ERROR"])
                
                message = None
                extra_fields = {}
                # Decide if this log should include metrics data based on level
                if level == "INFO":
                    if random.random() < 0.3:  # 30% of INFO logs include metrics
                        template, fields = random.choice(self.metrics_info_templates)
                        # Generate random values for placeholders
                        cpu_val = random.randint(0, 100)
                        mem_val = random.randint(100, 16000)       # memory in MB
                        status_val = random.choice(["Running", "Pending", "Succeeded"])
                        ready_val = random.choice([True, False])
                        pod_name_val = f"{app.replace(' ', '_')}-pod-{random.randint(1, 9999):04d}"
                        # Fill in the template
                        message = template.format(cpu=cpu_val, mem=mem_val, 
                                                  status=status_val, ready=str(ready_val), 
                                                  pod=pod_name_val, host=host)
                        # Add corresponding fields to extra_fields
                        if "cpu" in fields:
                            extra_fields["cpu"] = cpu_val
                        if "memory" in fields:
                            extra_fields["memory"] = mem_val
                        if "pod_status" in fields:
                            extra_fields["pod_status"] = status_val
                        if "ready" in fields:
                            extra_fields["ready"] = ready_val
                        if "pod_name" in fields:
                            extra_fields["pod_name"] = pod_name_val
                    else:
                        message = random.choice(self.normal_info_messages)
                elif level == "WARNING":
                    if random.random() < 0.3:  # 30% of WARNING logs include metrics
                        template, fields = random.choice(self.metrics_warning_templates)
                        cpu_val = random.randint(50, 100)         # high CPU if warning
                        mem_val = random.randint(1000, 16000)     # memory in MB
                        status_val = random.choice(["Pending", "CrashLoopBackOff"])
                        pod_name_val = f"{app.replace(' ', '_')}-pod-{random.randint(1, 9999):04d}"
                        message = template.format(cpu=cpu_val, mem=mem_val, 
                                                  status=status_val, pod=pod_name_val, host=host)
                        if "cpu" in fields:
                            extra_fields["cpu"] = cpu_val
                        if "memory" in fields:
                            extra_fields["memory"] = mem_val
                        if "pod_status" in fields:
                            extra_fields["pod_status"] = status_val
                        if "pod_name" in fields:
                            extra_fields["pod_name"] = pod_name_val
                    else:
                        message = random.choice(self.normal_warning_messages)
                else:  # level == "ERROR"
                    if random.random() < 0.2:  # 20% of ERROR logs include metrics
                        template, fields = random.choice(self.metrics_error_templates)
                        cpu_val = random.randint(80, 100)
                        mem_val = random.randint(2000, 16000)
                        status_val = random.choice(["CrashLoopBackOff", "Error", "Failed"])
                        pod_name_val = f"{app.replace(' ', '_')}-pod-{random.randint(1, 9999):04d}"
                        message = template.format(cpu=cpu_val, mem=mem_val, 
                                                  status=status_val, pod=pod_name_val, host=host)
                        if "cpu" in fields:
                            extra_fields["cpu"] = cpu_val
                        if "memory" in fields:
                            extra_fields["memory"] = mem_val
                        if "pod_status" in fields:
                            extra_fields["pod_status"] = status_val
                        if "pod_name" in fields:
                            extra_fields["pod_name"] = pod_name_val
                    else:
                        message = random.choice(self.normal_error_messages)
                
                # Construct the log entry dictionary
                log_entry = {
                    "type": "log",
                    "timestamp": ts_str,
                    "level": level,
                    "host": host,
                    "message": message,
                    "tags": [f"app:{app}", f"app_id:{self.apps[app]}"]
                }
                # Include any additional metrics fields in the log entry
                for key, val in extra_fields.items():
                    log_entry[key] = val
                self.data.append(log_entry)
            
            # --- Generate event entries for this app ---
            event_templates = [
                ("Deployment started", f"Deploying new version of {app} to production.", "info", "normal"),
                ("Deployment succeeded", f"{app} deployed successfully to production.", "success", "normal"),
                ("Deployment failed", f"{app} deployment failed during rollout.", "error", "normal"),
                ("High CPU Usage Alert", f"CPU usage for {app} exceeded 90% on {{host}}.", "warning", "normal"),
                ("Error Rate Spike", f"Error rate for {app} above 5% in the last 5 minutes.", "error", "normal"),
                ("Auto-scaling", f"{app} scaled up to {{instances}} instances due to load.", "info", "normal"),
                ("User Sign-Up", f"New user registered in {app}.", "info", "low"),
                ("Scheduled Maintenance", f"Maintenance scheduled for {app} at 12:00 AM UTC.", "info", "low"),
                ("Database Outage", f"{app} lost connection to database cluster.", "error", "normal"),
                ("Service Restored", f"{app} service restored after outage.", "success", "normal"),
            ]
            num_events = random.randint(5, 10)
            for _ in range(num_events):
                offset_seconds = random.random() * (self.days * 24 * 3600)
                ts = now - timedelta(seconds=offset_seconds)
                ts_str = ts.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
                host = random.choice(hosts)
                # Pick a random event template and fill placeholders
                title, text_template, alert_type, priority = random.choice(event_templates)
                # Fill in {host} or {instances} placeholders if present
                if "{host}" in text_template:
                    text_filled = text_template.format(host=host)
                elif "{instances}" in text_template:
                    instances_val = random.randint(2, 10)
                    text_filled = text_template.format(instances=instances_val)
                else:
                    text_filled = text_template
                # Construct the event entry
                event_entry = {
                    "type": "event",
                    "timestamp": ts_str,
                    "title": title,
                    "text": text_filled,
                    "host": host,
                    "tags": [f"app:{app}", f"app_id:{self.apps[app]}"],
                    "alert_type": alert_type,
                    "priority": priority
                }
                self.data.append(event_entry)
        # Sort all entries by timestamp for chronological order
        self.data.sort(key=lambda x: x["timestamp"])
    
    def get_data(self, app_name, days):
        """
        Retrieve logs and events for the given application name within the last `days` days.
        
        :param app_name: The name of the application to filter by.
        :param days: Number of days to look back from today (current UTC time).
        :return: List of log/event entry dictionaries for the app within the time window.
        """
        app_name_str = str(app_name)
        now = datetime.utcnow()
        cutoff_time = now - timedelta(days=days)
        result = []
        #print(f"Fetching logs for app: {app_name} with cutoff time: {self.data}")
        for entry in self.data:
            # Check if this entry belongs to the given app
            if any(tag == f"app:{app_name_str}" for tag in entry.get("tags", [])):
                # Parse the timestamp string to datetime for comparison
                try:
                    entry_time = datetime.strptime(entry["timestamp"], "%Y-%m-%dT%H:%M:%S.%fZ")
                except ValueError:
                    entry_time = datetime.strptime(entry["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
                if entry_time >= cutoff_time:
                    result.append(entry)
        return result
