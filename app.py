from flask import Flask, render_template, request, send_file
from PIL import Image, ImageDraw, ImageFont
import csv, os, zipfile, io, tempfile

app = Flask(__name__)

def get_font(size):
    # Linux server la Windows font irukathu, so default use pannuvom
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except:
        try:
            return ImageFont.truetype("arial.ttf", size)
        except:
            return ImageFont.load_default()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    template_file = request.files.get('template')
    csv_file = request.files.get('csv')
    y_pos = int(request.form.get('y_pos', 442))
    font_size = int(request.form.get('font_size', 54))
    r = int(request.form.get('color_r', 13))
    g = int(request.form.get('color_g', 35))
    b = int(request.form.get('color_b', 88))

    if not template_file or not csv_file:
        return "Upload both files", 400

    font = get_font(font_size)
    zip_buffer = io.BytesIO()
    
    # Read CSV
    csv_content = csv_file.read().decode('utf-8').splitlines()
    reader = csv.reader(csv_content)
    
    # Check header - if first row is "name" skip it
    rows = list(reader)
    if rows and rows[0][0].lower().strip() == 'name':
        rows = rows[1:]

    with zipfile.ZipFile(zip_buffer, 'w') as zipf:
        template_img_original = Image.open(template_file.stream).convert("RGB")
        for row in rows:
            if not row: continue
            name = row[0].strip()
            if not name: continue
            
            img = template_img_original.copy()
            draw = ImageDraw.Draw(img)
            W, H = img.size
            
            upper_name = name.upper()
            bbox = draw.textbbox((0,0), upper_name, font=font)
            text_w = bbox[2] - bbox[0]
            x = (W - text_w) / 2
            
            draw.text((x, y_pos), upper_name, font=font, fill=(r,g,b))
            
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='JPEG', quality=95)
            safe = "".join(c if c.isalnum() else "_" for c in name)
            zipf.writestr(f"{safe}.jpg", img_bytes.getvalue())

    zip_buffer.seek(0)
    return send_file(zip_buffer, as_attachment=True, download_name="OASYS_Certificates.zip", mimetype="application/zip")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)