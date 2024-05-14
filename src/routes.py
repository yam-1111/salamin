from flask import url_for, render_template, request, jsonify, send_file
from datetime import datetime, timedelta
import hashlib
import os
import requests


def init_app(app):
    DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "secure_downloads")
    SECRET_KEY = '12345'
    EXPIRATION_DELTA = timedelta(hours=1)
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    @app.route("/")
    def index():
        return render_template("webui.html", title_name="Salamin")

    @app.post("/download")
    def download():
        download_link = request.form.get("download_link")
        if not download_link or not download_link.startswith(("http://", "https://")):
            return jsonify({"download": "Invalid download link format"}), 400

        try:
            response = requests.get(download_link, stream=True)
            response.raise_for_status()  # Raise an exception for HTTP errors
        except requests.exceptions.RequestException as e:
            return jsonify({"download": f"Download failed: {e}"}), 500

        filename = os.path.basename(download_link)
        download_path = os.path.join(DOWNLOAD_DIR, filename)
        expiration_timestamp = (datetime.utcnow() + EXPIRATION_DELTA).strftime('%Y-%m-%dT%H:%M:%SZ')
        link_hash = hashlib.sha256((filename + expiration_timestamp + SECRET_KEY).encode()).hexdigest()
        download_link = f'/download_link/{filename}?ts={expiration_timestamp}&hash={link_hash}'

        with open(download_path, "wb") as f:
            for chunk in response.iter_content(1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)

        return jsonify(
            {
                "message": "Download complete. Use the provided link to download:",
                "download_link": download_link,
            }
        )
    
    @app.route('/download_link/<filename>')
    def download_link(filename):
        # Validate download link parameters
        try:
            expiration_timestamp = datetime.strptime(request.args.get('ts'), '%Y-%m-%dT%H:%M:%SZ')
            link_hash = request.args.get('hash')
            expected_hash = hashlib.sha256((filename + expiration_timestamp.strftime('%Y-%m-%dT%H:%M:%SZ') + SECRET_KEY).encode()).hexdigest()
        except (ValueError, KeyError):
            return jsonify({'error': 'Invalid download link parameters'}), 400

        # Check link expiration
        if expiration_timestamp < datetime.utcnow():
            return jsonify({'error': 'Download link expired'}), 400

        # Validate link hash
        if link_hash != expected_hash:
            return jsonify({'error': 'Invalid download link hash'}), 400

        # Construct the secure download path
        download_path = os.path.join(DOWNLOAD_DIR, filename)

        # (Optional) Check if file still exists
        # if not os.path.exists(download_path):
        #     return jsonify({'error': 'File not found'}), 404

        # Use Flask's send_file to deliver the download (consider security implications)
        return send_file(download_path, as_attachment=True)
