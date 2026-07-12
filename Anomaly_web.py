"""
Anomaly Web Dashboard
Flask-based control panel for the AnomalyOperator.
Provides visibility into registry, execution history, scheduling, and health.
"""

from flask import Flask, render_template_string, jsonify, request, send_file
from anomaly_scheduler import AnomalyOperator
from datetime import datetime
import json
import io


def create_app(operator: AnomalyOperator, debug=False):
    """Factory function to create and configure the Flask app."""
    app = Flask(__name__)
    app.config['JSON_SORT_KEYS'] = False

    @app.route('/api/health', methods=['GET'])
    def api_health():
        return jsonify(operator.system_health())

    @app.route('/api/registry', methods=['GET'])
    def api_registry():
        automations = []
        for name, a in operator.registry.items():
            automations.append({
                'name': name,
                'language': a.language,
                'deprecated': a.deprecated,
                'replaced_by': a.replaced_by,
                '
