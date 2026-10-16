#!/usr/bin/env python3
"""
PetroBPM & Soyuz MS 3D Unified Web Studio Server
================================================
Serves:
  - Interactive Web Studio UI (`/` -> `web/index.html`)
  - 3D Wavefront OBJ & MTL model + PBR Textures (`/assets/...`)
  - REST API for Oil & Gas Business Process Creation & Suitability Testing (Python + Java 21 Core):
      GET/POST `/api/bpm/evaluate` — Runs the Java 21 + Python suitability & Monte Carlo engine
      GET      `/api/bpm/bpmn`     — Exports BPMN 2.0 XML workflow definition
      GET      `/api/source-files` — Returns source code of Cinema 4D script, Java BPM engine, and Windows Installer scripts
      POST     `/api/model/rebuild`— Rebuilds 3D OBJ/MTL, PBR textures, and Windows Auto-Installer EXE
      GET      `/health`           — Health check endpoint
"""

import os
import json
import urllib.parse
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

from python_engine.bpm_orchestrator import run_java_bpm_engine, export_bpmn_xml
from python_engine.generate_soyuz_3d import generate_textures, build_soyuz_spacecraft, generate_c4d_script
from python_engine.build_installer_exe import build_packages

BASE_DIR = "/home/user/webapp"
PORT = int(os.environ.get("PORT", "8080"))


class StudioRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def _send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        qs = urllib.parse.parse_qs(parsed.query)

        if path in ("/", "/index.html"):
            self.path = "/web/index.html"
            return super().do_GET()

        if path == "/health":
            return self._send_json({
                "status": "ok",
                "service": "PetroBPM Oil & Gas Suitability + Soyuz MS 3D Studio",
                "javaEngine": "Java 21 OpenJDK Core",
                "pythonEngine": "Python 3.13 Orchestrator",
            })

        if path == "/api/bpm/evaluate":
            scenario = qs.get("scenario", ["nominal"])[0]
            feed_scale = float(qs.get("feedScale", ["1.0"])[0])
            sludge_factor = float(qs.get("sludgeFactor", ["1.0"])[0])
            monte_carlo = int(qs.get("monteCarlo", ["1000"])[0])
            try:
                res = run_java_bpm_engine(
                    scenario=scenario,
                    feed_scale=feed_scale,
                    sludge_factor=sludge_factor,
                    monte_carlo=monte_carlo,
                )
                return self._send_json(res)
            except Exception as e:
                return self._send_json({"error": str(e)}, status=500)

        if path == "/api/bpm/bpmn":
            scenario = qs.get("scenario", ["nominal"])[0]
            try:
                res = run_java_bpm_engine(scenario=scenario)
                xml_str = export_bpmn_xml(res)
                body = xml_str.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/xml; charset=utf-8")
                self.send_header("Content-Disposition", 'attachment; filename="petrobpm_oilgas_workflow.bpmn.xml"')
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return
            except Exception as e:
                return self._send_json({"error": str(e)}, status=500)

        if path == "/api/source-files":
            def read_safe(rel_p):
                fp = os.path.join(BASE_DIR, rel_p)
                if os.path.exists(fp):
                    with open(fp, "r", encoding="utf-8") as f:
                        return f.read()
                return ""

            return self._send_json({
                "c4d_script": read_safe("c4d_plugin/c4d_soyuz_generator.py"),
                "java_engine": read_safe("java_engine/src/com/petrobpm/OilGasBpmEngine.java"),
                "inno_setup": read_safe("installer/PetroBPM_Soyuz3D_Setup.iss"),
                "windows_bat": read_safe("installer/Run_PetroBPM_Studio.bat"),
                "mtl_file": read_safe("assets/model/soyuz_spacecraft.mtl"),
            })

        return super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        content_len = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_len).decode("utf-8") if content_len > 0 else "{}"
        try:
            data = json.loads(raw_body) if raw_body.strip() else {}
        except Exception:
            data = {}

        if path == "/api/bpm/evaluate":
            scenario = data.get("scenario", "nominal")
            feed_scale = float(data.get("feedScale", 1.0))
            sludge_factor = float(data.get("sludgeFactor", 1.0))
            monte_carlo = int(data.get("monteCarlo", 1000))
            custom_caps = data.get("customCapacities", {})
            try:
                res = run_java_bpm_engine(
                    scenario=scenario,
                    feed_scale=feed_scale,
                    sludge_factor=sludge_factor,
                    monte_carlo=monte_carlo,
                    custom_caps=custom_caps,
                )
                return self._send_json(res)
            except Exception as e:
                return self._send_json({"error": str(e)}, status=500)

        if path == "/api/model/rebuild":
            try:
                generate_textures()
                obj_p, mtl_p, n_v, n_f = build_soyuz_spacecraft()
                generate_c4d_script()
                c4d_zip, exe_p = build_packages()
                return self._send_json({
                    "status": "rebuilt",
                    "vertices": n_v,
                    "faces": n_f,
                    "objSizeKb": round(os.path.getsize(obj_p) / 1024, 1),
                    "exeSizeKb": round(os.path.getsize(exe_p) / 1024, 1),
                })
            except Exception as e:
                return self._send_json({"error": str(e)}, status=500)

        return self._send_json({"error": "Not found"}, status=404)


if __name__ == "__main__":
    os.chdir(BASE_DIR)
    # Ensure packages exist on startup
    build_packages()
    server = ThreadingHTTPServer(("0.0.0.0", PORT), StudioRequestHandler)
    print(f"[*] PetroBPM + Soyuz MS 3D Studio Server listening on http://0.0.0.0:{PORT}")
    server.serve_forever()
