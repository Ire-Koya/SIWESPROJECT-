import sys
import nmap
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class PortScannerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.nm = nmap.PortScanner()

    def initUI(self):
        self.setWindowTitle("Port and Vulnerability Scanner")
        self.resize(1200, 600)  # Increase window size for better display

        # Layouts
        layout = QVBoxLayout()
        input_layout = QHBoxLayout()

        # Input fields
        self.range_input = QLineEdit(self)
        self.range_input.setPlaceholderText("Enter network range, IP, or URL")
        input_layout.addWidget(QLabel("Target:"))
        input_layout.addWidget(self.range_input)

        # Scan Button
        scan_button = QPushButton("Start Scan")
        scan_button.clicked.connect(self.start_scan)
        input_layout.addWidget(scan_button)

        layout.addLayout(input_layout)

        # Result Table
        self.result_table = QTableWidget(0, 5)
        self.result_table.setHorizontalHeaderLabels(["IP Address", "Port", "Service", "State", "CVE"])
        self.result_table.horizontalHeader().setFont(QFont("Arial", 12, QFont.Bold))  # Increase header font size

        # Set column widths
        self.result_table.setColumnWidth(0, 150)
        self.result_table.setColumnWidth(1, 100)
        self.result_table.setColumnWidth(2, 150)
        self.result_table.setColumnWidth(3, 100)
        self.result_table.setColumnWidth(4, 500)  # Increase CVE column width to display longer links

        layout.addWidget(self.result_table)
        self.setLayout(layout)

    def start_scan(self):
        target = self.range_input.text()
        self.result_table.setRowCount(0)  # Clear previous results

        if "/" in target:  # Network range
            self.nm.scan(hosts=target, arguments="-p 1-10000 --script vuln")
        elif "." in target:  # IP address
            self.nm.scan(hosts=target, arguments="-p 1-10000 --script vuln")
        else:  # URL assumed
            ip_address = socket.gethostbyname(target)
            self.nm.scan(hosts=ip_address, arguments="-p 1-10000 --script vuln")

        self.process_scan_results()

    def process_scan_results(self):
        for host in self.nm.all_hosts():
            ip = host
            for proto in self.nm[host].all_protocols():
                ports = self.nm[host][proto].keys()
                for port in ports:
                    service = self.nm[host][proto][port].get('name', 'unknown')
                    state = self.nm[host][proto][port]['state']
                    cve_ids = self.extract_cves_from_vuln_scan(host, proto, port)

                    row_position = self.result_table.rowCount()
                    self.result_table.insertRow(row_position)
                    self.result_table.setItem(row_position, 0, QTableWidgetItem(ip))
                    self.result_table.setItem(row_position, 1, QTableWidgetItem(str(port)))
                    self.result_table.setItem(row_position, 2, QTableWidgetItem(service))
                    self.result_table.setItem(row_position, 3, QTableWidgetItem(state))
                    self.result_table.setItem(row_position, 4, QTableWidgetItem(", ".join(cve_ids) if cve_ids else "None"))

    def extract_cves_from_vuln_scan(self, host, proto, port):
        """Extracts CVE IDs from the vulnerability scan results."""
        cve_list = []
        if 'script' in self.nm[host][proto][port]:
            vuln_output = self.nm[host][proto][port]['script']
            for script_name, output in vuln_output.items():
                if "CVE-" in output:
                    cves = [line.split()[0] for line in output.splitlines() if "CVE-" in line]
                    cve_list.extend(cves)
        return cve_list

app = QApplication(sys.argv)
scanner = PortScannerApp()
scanner.show()
sys.exit(app.exec_())

