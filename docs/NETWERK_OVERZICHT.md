# Netwerk Verbinding Overzicht

Overzicht van alle netwerk verbindingsmethoden voor de Go2 robot.

## Verbindingsmethoden

| Methode | Gebruik | Documentatie |
|---------|---------|--------------|
| **Ethernet** | Directe verbinding, meest stabiel | [ETHERNET_VERBINDING.md](./ETHERNET_VERBINDING.md) |
| **WiFi** | Wireless via ingebouwde WiFi | [WIFI_VERBINDING.md](./WIFI_VERBINDING.md) |
| **USB WiFi Dongle** | Extra WiFi adapter | [USB_WIFI_DONGLE.md](./USB_WIFI_DONGLE.md) |

## Quick Reference

### Standaard IP Adressen

| Verbinding | Robot IP | Computer IP |
|------------|----------|-------------|
| Direct Ethernet | `192.168.123.161` | `192.168.123.222` |
| Via Router | DHCP (bijv. `192.168.1.x`) | DHCP |
| Robot AP Mode | `192.168.123.1` | Automatisch |

### Belangrijke Poorten

| Poort | Protocol | Gebruik |
|-------|----------|---------|
| `8080` | UDP | Custom SDK communicatie |
| `7400-7500` | UDP | DDS (officiële SDK) |
| `239.255.0.1` | Multicast | DDS discovery |

## Aanbevolen Volgorde

1. **Eerste setup**: Probeer [Ethernet](./ETHERNET_VERBINDING.md) (meest betrouwbaar)
2. **Wireless nodig**: Probeer [WiFi](./WIFI_VERBINDING.md)
3. **WiFi problemen**: Probeer [USB WiFi Dongle](./USB_WIFI_DONGLE.md)

## Troubleshooting

- **Firewall problemen**: Zie [FIREWALL_TROUBLESHOOTING.md](./FIREWALL_TROUBLESHOOTING.md)
- **Kan niet pingen**: Check fysieke verbinding en IP configuratie
- **SDK werkt niet**: Check poorten en firewall instellingen

## Netwerk Interface Namen

### macOS
```bash
ifconfig | grep -B 1 "192.168.123"
# Interface naam: en0, en5, enxf8e43b808e06, etc.
```

### Linux
```bash
ip addr show | grep -B 2 "192.168.123"
# Interface naam: eth0, enp1s0, wlan0, etc.
```

## Referenties

- [First Time Setup](./FIRST_TIME_SETUP.md)
- [Go2 Handleiding](./GO2_HANDLEIDING.md)


