#!/usr/bin/env python3
"""
RS41-NFW Detailed Telemetry Capture & Analysis
Captures all telemetry data from the sonde serial port
"""

import serial
import time
import json
from datetime import datetime

PORT = 'COM8'
BAUD = 115200
CAPTURE_TIME = 30  # seconds

def parse_telemetry_line(line):
    """Parse telemetry line with format: KEY: VALUE"""
    if ':' not in line:
        return None
    
    parts = line.split(':', 1)
    if len(parts) == 2:
        key = parts[0].strip().replace('[info] ', '').replace('[ERR] ', '')
        value = parts[1].strip()
        return {key: value}
    return None

def main():
    try:
        print("=" * 70)
        print("RS41-NFW DETAILED TELEMETRY CAPTURE")
        print("=" * 70)
        print(f"🔌 Conectando em {PORT} @ {BAUD} baud\n")
        
        ser = serial.Serial(PORT, BAUD, timeout=1)
        time.sleep(1)
        
        telemetry_data = {}
        info_logs = []
        error_logs = []
        
        start_time = time.time()
        
        print(f"📊 Capturando dados por {CAPTURE_TIME} segundos...\n")
        print("-" * 70)
        
        while time.time() - start_time < CAPTURE_TIME:
            if ser.in_waiting:
                try:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    
                    if not line:
                        continue
                    
                    # Separar dados estruturados de logs
                    if '[info]' in line:
                        info_logs.append(line)
                        print(f"ℹ️  {line}")
                    elif '[ERR]' in line or '[error]' in line or '[ERROR]' in line:
                        error_logs.append(line)
                        print(f"❌ {line}")
                    elif ':' in line:
                        # Dados estruturados de telemetria
                        parsed = parse_telemetry_line(line)
                        if parsed:
                            telemetry_data.update(parsed)
                            key = list(parsed.keys())[0]
                            val = parsed[key]
                            print(f"📡 {key:30s} : {val}")
                    else:
                        print(f"└─ {line}")
                        
                except Exception as e:
                    print(f"⚠️  Erro ao processar: {e}")
            
            time.sleep(0.01)
        
        ser.close()
        
        print("\n" + "=" * 70)
        print("RESUMO DA CAPTURA")
        print("=" * 70)
        
        print(f"\n📊 TELEMETRIA ESTRUTURADA ({len(telemetry_data)} parâmetros):")
        print("-" * 70)
        for key, value in sorted(telemetry_data.items()):
            print(f"  {key:35s} : {value}")
        
        print(f"\n📋 LOGS DE INFORMAÇÃO ({len(info_logs)} mensagens):")
        print("-" * 70)
        for log in info_logs[:10]:  # Primeiras 10
            print(f"  {log}")
        if len(info_logs) > 10:
            print(f"  ... e mais {len(info_logs) - 10} mensagens")
        
        if error_logs:
            print(f"\n❌ ERROS DETECTADOS ({len(error_logs)} mensagens):")
            print("-" * 70)
            for log in error_logs:
                print(f"  {log}")
        else:
            print(f"\n✅ Nenhum erro detectado")
        
        # Salvar em JSON
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"telemetry_{timestamp}.json"
        
        output_data = {
            "timestamp": datetime.now().isoformat(),
            "telemetry": telemetry_data,
            "info_logs": info_logs,
            "error_logs": error_logs,
            "summary": {
                "total_telemetry_params": len(telemetry_data),
                "total_info_logs": len(info_logs),
                "total_errors": len(error_logs),
                "capture_duration_seconds": int(time.time() - start_time)
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Dados salvos em: {output_file}")
        print("\n" + "=" * 70)
        
    except serial.SerialException as e:
        print(f"❌ Erro de porta serial: {e}")
        print(f"Verifique se a porta {PORT} está conectada corretamente")
    except Exception as e:
        print(f"❌ Erro geral: {e}")

if __name__ == "__main__":
    main()
