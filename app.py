from flask import Flask, render_template, jsonify
import psutil
import time
import subprocess
import platform

app = Flask(__name__)

def get_wifi_status():
    # 1. Hitung total riwayat data terpakai (dalam Megabytes)
    net_io = psutil.net_io_counters()
    total_mb = (net_io.bytes_sent + net_io.bytes_recv) / (1024 * 1024)
    
    # 2. Cek Latency / Ping untuk deteksi lag (Ping ke DNS Google)
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', '8.8.8.8']
    
    start_time = time.time()
    try:
        # Menjalankan perintah ping
        ping_received = subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
        latency = round((time.time() - start_time) * 1000, 2) if ping_received else 999
    except Exception:
        latency = 999
    
    # Status berdasarkan latency
    if latency > 150:
        status = "Lagging"
    elif latency == 999:
        status = "RTO / Disconnect"
    else:
        status = "Stabil"

    return {
        "ping_ms": latency,
        "total_data_mb": round(total_mb, 2),
        "status": status
    }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/wifi')
def api_wifi():
    return jsonify(get_wifi_status())

# Bagian ini penting agar bisa dijalankan lokal maupun di Vercel
if __name__ == '__main__':
    app.run(debug=True)
