import os
import sys
import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import webview

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import joblib
import numpy as np
from src.predict import predict_gesture_top_distribution
from src.model_utils import load_model, load_scaler

# Pre-load model artifacts
model = load_model()
scaler = load_scaler()
test_data_path = os.path.join(PROJECT_ROOT, "models", "test_data.pkl")
if os.path.exists(test_data_path):
    X_test_scaled, y_test, _ = joblib.load(test_data_path)
else:
    X_test_scaled, y_test = None, None

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>SVM-RBF Sign Language Predictor</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    body { background-color: #030712; color: #f9fafb; font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; user-select: none; }
    .glass-card { background: #0b1329; border: 1px solid #1e293b; border-radius: 1rem; }
    .neon-border { border: 1px solid #0284c7; box-shadow: 0 0 15px rgba(2, 132, 199, 0.25); }
    .glow-circle {
      width: 220px; height: 220px; border-radius: 50%;
      background: radial-gradient(circle, #022c22 0%, #061923 70%, #0b1329 100%);
      border: 3px solid #22c55e;
      box-shadow: 0 0 35px rgba(34, 197, 94, 0.4), inset 0 0 25px rgba(34, 197, 94, 0.2);
    }
    .btn-gradient {
      background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%);
      box-shadow: 0 4px 15px rgba(79, 70, 229, 0.4);
    }
    .btn-gradient:hover {
      background: linear-gradient(135deg, #4338ca 0%, #2563eb 100%);
      box-shadow: 0 4px 20px rgba(79, 70, 229, 0.6);
    }
  </style>
</head>
<body class="p-6 min-h-screen flex flex-col justify-between">
  
  <!-- Header Navbar -->
  <header class="flex items-center justify-between pb-4">
    <div class="flex items-center space-x-3">
      <button class="bg-[#111c38] hover:bg-[#1a294f] text-cyan-400 text-sm font-semibold px-4 py-2 rounded-lg border border-slate-700 transition flex items-center gap-2">
        <i class="fa-solid fa-house text-xs"></i> Dashboard
      </button>
    </div>
    <div class="text-center">
      <div class="flex items-center justify-center gap-2">
        <i class="fa-solid fa-brain text-blue-400 text-2xl"></i>
        <h1 class="text-2xl font-bold text-blue-400 tracking-wide">SVM-RBF Sign Language Predictor</h1>
      </div>
      <p class="text-xs text-slate-400 tracking-wider mt-0.5">Core ML Engine &nbsp;•&nbsp; Real-Time Inference Inspector</p>
    </div>
    <div class="flex items-center space-x-3">
      <div class="bg-[#111c38] text-slate-300 text-xs px-3 py-1.5 rounded-lg border border-slate-700 flex items-center gap-2">
        <i class="fa-solid fa-moon"></i> Dark
      </div>
      <div class="bg-[#052e16] text-green-400 text-xs font-semibold px-3 py-1.5 rounded-lg border border-green-800 flex items-center gap-2">
        <span class="h-2 w-2 rounded-full bg-green-400 animate-pulse"></span> Model Online
      </div>
    </div>
  </header>

  <!-- Section 1: Sensor Input Vector -->
  <section class="glass-card p-5 my-2">
    <div class="flex items-center space-x-3 mb-3">
      <span class="bg-[#1e293b] text-white text-xs font-bold px-2.5 py-1 rounded">1</span>
      <div>
        <h2 class="text-sm font-bold text-white uppercase tracking-wider">Sensor Input Vector (12 Channels)</h2>
        <p class="text-xs text-slate-400">Enter 12 channel values (comma or space separated)</p>
      </div>
    </div>
    <div class="neon-border bg-[#050a17] rounded-xl px-4 py-3 flex items-center space-x-3">
      <i class="fa-solid fa-wave-square text-cyan-400"></i>
      <input id="sensorInput" type="text" value="0.12, 0.45, 0.32, 0.11, 0.09, 9.81, 0.02, 0.15, 1.2, 0.3, 0.5, 25.4"
             class="bg-transparent text-cyan-300 font-mono text-sm flex-1 outline-none">
      <i class="fa-regular fa-circle-check text-green-400 text-lg"></i>
    </div>
    <div class="flex justify-between items-center mt-4">
      <button onclick="loadRandomSample()" class="bg-[#111c38] hover:bg-[#1a294f] text-slate-200 text-xs font-semibold px-4 py-2.5 rounded-lg border border-slate-700 transition flex items-center gap-2">
        <i class="fa-solid fa-dice"></i> Load Random Test Sample
      </button>
      <button onclick="classifyGesture()" class="btn-gradient text-white text-sm font-bold px-6 py-2.5 rounded-lg transition flex items-center gap-2">
        <i class="fa-solid fa-bolt"></i> Classify Gesture
      </button>
    </div>
  </section>

  <!-- Section 2: Split Telemetry & Results -->
  <div class="grid grid-cols-12 gap-5 my-2">
    <!-- Left Column: System Status -->
    <div class="col-span-3 glass-card p-5 flex flex-col justify-between">
      <div class="flex items-center space-x-2 mb-4">
        <h3 class="text-xs font-bold text-white uppercase tracking-wider">System Status</h3>
        <span class="h-2 w-2 rounded-full bg-green-400"></span>
      </div>
      <div class="space-y-3">
        <div class="bg-[#091024] p-3 rounded-xl border border-slate-800 flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div class="bg-emerald-950 p-2 rounded-lg text-emerald-400"><i class="fa-solid fa-cube text-xs"></i></div>
            <div>
              <div class="text-[10px] text-slate-400">Model</div>
              <div class="text-xs font-bold text-slate-200">SVM-RBF Classifier</div>
            </div>
          </div>
          <i class="fa-solid fa-check text-green-400 text-xs"></i>
        </div>

        <div class="bg-[#091024] p-3 rounded-xl border border-slate-800 flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div class="bg-blue-950 p-2 rounded-lg text-cyan-400"><i class="fa-solid fa-bolt text-xs"></i></div>
            <div>
              <div class="text-[10px] text-slate-400">Status</div>
              <div class="text-xs font-bold text-slate-200">Model Loaded & Ready</div>
            </div>
          </div>
          <i class="fa-solid fa-check text-green-400 text-xs"></i>
        </div>

        <div class="bg-[#091024] p-3 rounded-xl border border-slate-800 flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div class="bg-purple-950 p-2 rounded-lg text-purple-400"><i class="fa-solid fa-microchip text-xs"></i></div>
            <div>
              <div class="text-[10px] text-slate-400">Engine</div>
              <div class="text-xs font-bold text-slate-200">Core ML Inference Engine</div>
            </div>
          </div>
          <i class="fa-solid fa-check text-green-400 text-xs"></i>
        </div>

        <div class="bg-[#091024] p-3 rounded-xl border border-slate-800 flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div class="bg-amber-950 p-2 rounded-lg text-amber-400"><i class="fa-solid fa-stopwatch text-xs"></i></div>
            <div>
              <div class="text-[10px] text-slate-400">Latency</div>
              <div id="statusLatency" class="text-xs font-bold text-slate-200">1.33 ms (avg)</div>
            </div>
          </div>
          <i class="fa-solid fa-check text-green-400 text-xs"></i>
        </div>

        <div class="bg-[#091024] p-3 rounded-xl border border-slate-800 flex items-center justify-between">
          <div class="flex items-center space-x-3">
            <div class="bg-cyan-950 p-2 rounded-lg text-cyan-400"><i class="fa-solid fa-clock text-xs"></i></div>
            <div>
              <div class="text-[10px] text-slate-400">Last Updated</div>
              <div id="statusUpdated" class="text-xs font-bold text-slate-200">Just now</div>
            </div>
          </div>
          <i class="fa-solid fa-check text-green-400 text-xs"></i>
        </div>
      </div>
    </div>

    <!-- Right Column: ML Classification Result Card -->
    <div class="col-span-9 glass-card p-6 flex flex-col justify-between">
      <div class="flex items-center space-x-3 mb-2">
        <span class="bg-[#1e293b] text-white text-xs font-bold px-2.5 py-1 rounded">2</span>
        <h2 class="text-sm font-bold text-white uppercase tracking-wider">ML Classification Result</h2>
      </div>

      <div class="grid grid-cols-12 gap-6 items-center">
        <!-- Center Dial & Badges -->
        <div class="col-span-7 flex flex-col items-center justify-center py-2">
          <div class="glow-circle flex flex-col items-center justify-center relative my-2">
            <span id="predChar" class="text-6xl font-black text-green-400 tracking-wider">B</span>
            <div class="mt-2 bg-[#064e3b] text-green-400 text-[10px] font-bold px-3 py-0.5 rounded-full border border-green-600">
              Predicted Gesture
            </div>
          </div>
          <div class="text-center mt-3">
            <div class="text-lg font-bold text-white">Confidence: <span id="predConf" class="text-green-400 font-extrabold">95.70%</span></div>
            <div id="predLatency" class="text-xs text-slate-400 mt-0.5"><i class="fa-solid fa-stopwatch mr-1"></i> Inference Latency: 1.33 ms</div>
          </div>
          <div class="mt-3 bg-[#052e16] border border-green-800 text-green-300 text-xs font-semibold px-5 py-1.5 rounded-full flex items-center gap-2">
            <i class="fa-solid fa-check"></i> Classification completed successfully <i class="fa-solid fa-wand-magic-sparkles text-[10px] ml-1"></i>
          </div>
        </div>

        <!-- Right: Top Predictions Bar Chart -->
        <div class="col-span-5 bg-[#070d1e] p-4 rounded-xl border border-slate-800 flex flex-col justify-between h-full">
          <div>
            <h4 class="text-xs font-bold text-slate-300 uppercase tracking-wider mb-3">Top Predictions</h4>
            <div id="probBarsContainer" class="space-y-3">
              <!-- Dynamically populated -->
            </div>
          </div>
          <button class="w-full mt-4 bg-[#111c38] hover:bg-[#1a294f] text-cyan-400 text-xs font-semibold py-2 rounded-lg border border-slate-700 transition flex items-center justify-center gap-2">
            <i class="fa-solid fa-chart-simple"></i> View Probability Distribution
          </button>
        </div>
      </div>
    </div>
  </div>

  <!-- Bottom Metric Cards -->
  <section class="grid grid-cols-5 gap-4 mt-2">
    <div class="glass-card p-4 border border-slate-800 flex items-start space-x-3">
      <div class="bg-purple-950/70 p-2 rounded-lg text-purple-400 mt-0.5"><i class="fa-solid fa-brain text-sm"></i></div>
      <div>
        <div class="text-xs font-bold text-white uppercase">SVM-RBF Model</div>
        <div class="text-[11px] text-slate-400 mt-1">Support Vector Machine<br>with RBF Kernel</div>
      </div>
    </div>

    <div class="glass-card p-4 border border-slate-800 flex items-start space-x-3">
      <div class="bg-blue-950/70 p-2 rounded-lg text-cyan-400 mt-0.5"><i class="fa-solid fa-crosshairs text-sm"></i></div>
      <div>
        <div class="text-xs font-bold text-white uppercase">High Accuracy</div>
        <div class="text-[11px] text-slate-400 mt-1">Trained for robust<br>gesture classification</div>
      </div>
    </div>

    <div class="glass-card p-4 border border-slate-800 flex items-start space-x-3">
      <div class="bg-amber-950/70 p-2 rounded-lg text-amber-400 mt-0.5"><i class="fa-solid fa-bolt text-sm"></i></div>
      <div>
        <div class="text-xs font-bold text-white uppercase">Real-Time</div>
        <div class="text-[11px] text-slate-400 mt-1">Ultra-fast inference<br>for real-time apps</div>
      </div>
    </div>

    <div class="glass-card p-4 border border-slate-800 flex items-start space-x-3">
      <div class="bg-cyan-950/70 p-2 rounded-lg text-cyan-400 mt-0.5"><i class="fa-solid fa-wave-square text-sm"></i></div>
      <div>
        <div class="text-xs font-bold text-white uppercase">12 Channels</div>
        <div class="text-[11px] text-slate-400 mt-1">Multi-sensor input<br>vector processing</div>
      </div>
    </div>

    <div class="glass-card p-4 border border-slate-800 flex items-start space-x-3">
      <div class="bg-emerald-950/70 p-2 rounded-lg text-emerald-400 mt-0.5"><i class="fa-solid fa-shield-halved text-sm"></i></div>
      <div>
        <div class="text-xs font-bold text-white uppercase">Secure & Reliable</div>
        <div class="text-[11px] text-slate-400 mt-1">Robust predictions with<br>high confidence</div>
      </div>
    </div>
  </section>

  <!-- Footer -->
  <footer class="text-center text-slate-500 text-xs mt-3">
    © 2026 Sign Language Predictor &nbsp;•&nbsp; Built with <span class="text-red-500">❤️</span> for Accessibility
  </footer>

  <script>
    async function classifyGesture() {
      const rawText = document.getElementById('sensorInput').value;
      const tokens = rawText.replace(/,/g, ' ').trim().split(/\\s+/).map(Number);

      const res = await fetch('/api/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ features: tokens })
      });
      const data = await res.json();
      if (data.error) {
        alert(data.error);
        return;
      }

      document.getElementById('predChar').innerText = data.prediction;
      document.getElementById('predConf').innerText = data.confidence + '%';
      document.getElementById('predLatency').innerHTML = '<i class="fa-solid fa-stopwatch mr-1"></i> Inference Latency: ' + data.latency_ms + ' ms';
      document.getElementById('statusLatency').innerText = data.latency_ms + ' ms (avg)';
      document.getElementById('statusUpdated').innerText = new Date().toLocaleTimeString();

      const container = document.getElementById('probBarsContainer');
      container.innerHTML = '';
      data.distribution.forEach((item, idx) => {
        const isTop = idx === 0;
        const barColor = isTop ? 'bg-green-400' : 'bg-blue-500';
        const row = `
          <div class="flex items-center justify-between text-xs">
            <span class="font-bold text-slate-200 w-8">${item.label}</span>
            <div class="flex-1 mx-3 bg-slate-800 h-2 rounded-full overflow-hidden">
              <div class="${barColor} h-full rounded-full transition-all duration-500" style="width: ${item.prob}%"></div>
            </div>
            <span class="text-slate-400 font-mono w-12 text-right">${item.prob.toFixed(2)}%</span>
          </div>
        `;
        container.innerHTML += row;
      });
    }

    async function loadRandomSample() {
      const res = await fetch('/api/random_sample');
      const data = await res.json();
      if (data.vector) {
        document.getElementById('sensorInput').value = data.vector;
        classifyGesture();
      }
    }

    window.onload = () => {
      classifyGesture();
    };
  </script>
</body>
</html>
"""

class RequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(DASHBOARD_HTML.encode("utf-8"))
        elif self.path == "/api/random_sample":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            if X_test_scaled is not None and len(X_test_scaled) > 0:
                idx = np.random.randint(0, len(X_test_scaled))
                raw_values = scaler.inverse_transform(X_test_scaled[idx : idx + 1])[0]
                formatted_str = ", ".join([f"{v:.2f}" for v in raw_values])
                self.wfile.write(json.dumps({"vector": formatted_str}).encode("utf-8"))
            else:
                self.wfile.write(json.dumps({"vector": "0.12, 0.45, 0.32, 0.11, 0.09, 9.81, 0.02, 0.15, 1.2, 0.3, 0.5, 25.4"}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/predict":
            length = int(self.headers.get("content-length", 0))
            body = self.rfile.read(length)
            data = json.loads(body)
            features = data.get("features", [])

            t0 = time.perf_counter()
            try:
                pred, conf, dist = predict_gesture_top_distribution(features, top_n=5)
                latency_ms = round((time.perf_counter() - t0) * 1000, 2)
                response = {
                    "prediction": pred,
                    "confidence": conf,
                    "latency_ms": latency_ms,
                    "distribution": dist
                }
            except Exception as e:
                response = {"error": str(e)}

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode("utf-8"))

def launch_dashboard(start_port=8080):
    port = start_port
    server = None
    
    while port < start_port + 50:
        try:
            server = HTTPServer(("127.0.0.1", port), RequestHandler)
            break
        except OSError:
            port += 1

    if server is None:
        print("Error: Could not bind to an open port.")
        return

    url = f"http://127.0.0.1:{port}"
    
    # Run the background HTTP handler for the webview window
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    
    # Launch as a standalone desktop pop-up application window
    window = webview.create_window(
        title="SVM-RBF Sign Language Predictor",
        url=url,
        width=1200,
        height=860,
        resizable=True,
        min_size=(1080, 780),
        background_color="#030712"
    )
    webview.start()
    
    server.shutdown()
    server.server_close()

if __name__ == "__main__":
    launch_dashboard()