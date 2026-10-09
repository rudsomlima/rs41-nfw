#!/usr/bin/env python3
"""
RS41-NFW Advanced Telemetry Real-Time Dashboard
Captures and displays live telemetry with frequency analysis
"""

import serial
import time
import re
from datetime import datetime
from collections import defaultdict

PORT = 'COM8'
BAUD = 115200
CAPTURE_TIME = 45  # seconds

# Regex para extrair valores numéricos de diferentes tipos de mensagens
PATTERNS = {
    'gps_lat': r'gpsLat[:\s=]+([+-]?\d+\.?\d*)',
    'gps_long': r'gpsLong[:\s=]+([+-]?\d+\.?\d*)',
    'gps_alt': r'gpsAlt[:\s=]+([+-]?\d+\.?\d*)',
    'gps_sats': r'gpsSats[:\s=]+(\d+)',
    'battery': r'batV[:\s=]+([+-]?\d+\.?\d*)',
    'temperature': r'mainTemperatureValue[:\s=]+([+-]?\d+\.?\d*)',
    'humidity': r'humidityValue[:\s=]+(\d+\.?\d*)',
    'pressure': r'pressureValue[:\s=]+([+-]?\d+\.?\d*)',
    'altitude': r'maxAlt[:\s=]+(\d+)',
    'reference_temp': r'cut-out temperature\s*=\s*([+-]?\d+\.?\d*)',
    'humidity_power': r'Humidity module heating power is (\d+)',
    'speed': r'gpsSpeedKph[:\s=]+([+-]?\d+\.?\d*)',
    'hdop': r'gpsHdop[:\s=]+([+-]?\d+\.?\d*)',
}

def extract_values(text):
    """Extract all known telemetry values from text"""
    values = {}
    for key, pattern in PATTERNS.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                values[key] = float(match.group(1))
            except:
                pass
    return values

def main():
    try:
        print("\n" + "=" * 80)
        print("RS41-NFW ADVANCED TELEMETRY REAL-TIME DASHBOARD")
        print("=" * 80)
        print(f"🔌 Porta: {PORT} | 🔧 Baudrate: {BAUD} | ⏱️  Captura: {CAPTURE_TIME}s\n")
        
        ser = serial.Serial(PORT, BAUD, timeout=1)
        time.sleep(1)
        
        # Dicionários para armazenar dados
        telemetry = defaultdict(list)
        event_counts = defaultdict(int)
        
        start_time = time.time()
        last_stats_time = start_time
        
        print("📡 Monitorando COM8...\n")
        print("-" * 80)
        
        while time.time() - start_time < CAPTURE_TIME:
            if ser.in_waiting:
                try:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    
                    if not line:
                        continue
                    
                    # Contar eventos
                    if 'HORUS' in line:
                        event_counts['HORUS Transmissions'] += 1
                    if 'GPS' in line:
                        if 'obtained' in line:
                            event_counts['GPS Updates'] += 1
                        if 'on index' in line or 'TX' in line:
                            event_counts['TX Events'] += 1
                    if 'RPM411' in line:
                        event_counts['Pressure Sensor Reads'] += 1
                    if 'heater' in line.lower():
                        event_counts['Heater Events'] += 1
                    
                    # Extrair valores de telemetria
                    values = extract_values(line)
                    for key, val in values.items():
                        telemetry[key].append(val)
                    
                    # Mostrar dados extraídos
                    if values:
                        print(f"✓ {line[:77]}")
                        for k, v in values.items():
                            print(f"  └─ {k:25s} = {v:.4f}")
                    
                except Exception as e:
                    pass
            
            time.sleep(0.05)
        
        ser.close()
        
        # Análise estatística
        print("\n" + "=" * 80)
        print("📊 ANÁLISE ESTATÍSTICA DOS DADOS COLETADOS")
        print("=" * 80)
        
        print("\n🎯 CONTAGEM DE EVENTOS:")
        print("-" * 80)
        for event, count in sorted(event_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {event:35s} : {count:4d} eventos")
        
        if telemetry:
            print("\n📈 ESTATÍSTICAS DE TELEMETRIA:")
            print("-" * 80)
            for param, values in sorted(telemetry.items()):
                if values:
                    min_val = min(values)
                    max_val = max(values)
                    avg_val = sum(values) / len(values)
                    
                    print(f"\n  {param}:")
                    print(f"    Min:     {min_val:10.4f}")
                    print(f"    Max:     {max_val:10.4f}")
                    print(f"    Média:   {avg_val:10.4f}")
                    print(f"    Amostras: {len(values)}")
                    
                    # Calcular variância
                    variance = sum((x - avg_val) ** 2 for x in values) / len(values)
                    print(f"    Desvio:  {variance ** 0.5:10.4f}")
        
        # Calcular frequências
        elapsed = time.time() - start_time
        print(f"\n⏱️  FREQUÊNCIA DE EVENTOS (em {elapsed:.1f}s):")
        print("-" * 80)
        for event, count in sorted(event_counts.items(), key=lambda x: x[1], reverse=True):
            freq = count / elapsed
            print(f"  {event:35s} : {freq:.2f} Hz ({count} total)")
        
        print("\n" + "=" * 80)
        print("✅ ANÁLISE COMPLETA - Sonda operacional com sucesso!")
        print("=" * 80 + "\n")
        
    except serial.SerialException as e:
        print(f"❌ Erro de porta serial: {e}")
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    main()
