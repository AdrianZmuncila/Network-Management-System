This project simulates an enterprise network infrastructure using GNS3, Cisco devices, Docker containers, Prometheus, Grafana, and Linux virtual machines.

The network topology and device configurations were designed and implemented in GNS3, while Ubuntu Server and Kali Linux were deployed as VirtualBox virtual machines integrated into the simulated network.

The purpose of the project is to demonstrate:

VLAN segmentation
Inter-VLAN routing
ACL security policies
Centralized DHCP and DNS
Network monitoring and observability
Artificial traffic generation
Infrastructure troubleshooting
Network Topology

The topology contains:

2 Cisco routers (R1, R2)
2 Ethernet switches
Ubuntu Server (VirtualBox VM)
Kali Linux client (VirtualBox VM)
Multiple VLANs
Internet connectivity through NAT

Main VLANs:

VLAN10 — IT
VLAN20 — HR
VLAN30 — Guests
VLAN40 — Servers

The entire topology was built and configured in GNS3, with VirtualBox used to host the Ubuntu Server and Kali Linux virtual machines connected to the network.
Routing and VLANs

Router-on-a-Stick was implemented on R1 using 802.1Q subinterfaces.

Example:

Fa0/0.10 → VLAN10
Fa0/0.20 → VLAN20
Fa0/0.30 → VLAN30
Fa0/0.40 → VLAN40

Trunk links were configured between switches and the router.

ACL Security Policies

ACLs were configured to restrict communication between departments.

Examples:

HR cannot access IT VLAN
Guests have restricted access
DNS and web access are permitted
DHCP and DNS Services

Ubuntu Server provides:

ISC DHCP Server
Bind9 DNS Server

Clients automatically receive:

IP address
Gateway
DNS configuration

Local domain:

firma.local
Monitoring Stack

Docker containers were deployed on Ubuntu Server:

Prometheus
Grafana
Alertmanager
Node Exporter
ML Detector

Prometheus collects metrics from Node Exporter.

Grafana visualizes:

CPU usage
RAM usage
Network traffic
System load
Throughput
Artificial Traffic Generation

Traffic was generated using iperf3.

Server:

iperf3 -s

Client:

iperf3 -c 192.168.40.10 -P 10 -t 120

This generated observable network spikes in Grafana dashboards.

Technologies Used
GNS3
Cisco IOS
Ubuntu Server
Kali Linux
Docker
Prometheus
Grafana
Alertmanager
Node Exporter
Bind9
ISC DHCP Server
iperf3
Screenshots

Include screenshots for:

GNS3 topology
Grafana dashboards
Prometheus targets
VLAN configuration
ACL configuration
iperf3 traffic generation
Future Improvements
SNMP monitoring
Syslog server
Email alerting
Anomaly detection improvements
VPN integration
Firewall integration
