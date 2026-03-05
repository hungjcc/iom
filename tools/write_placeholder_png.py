import base64
from pathlib import Path

# Small visible placeholder PNG (18x18 gray square) encoded in base64
b64 = (
    "iVBORw0KGgoAAAANSUhEUgAAABIAAAASCAYAAABWzo5XAAAACXBIWXMAAAsTAAALEwEAmpwYAAAB"
    "H0lEQVQ4y+2UPUoDQRSGv3M0gqKCiK2kF0cR0bGwUq2lrY2Fhb2Dk7u7u7s7T0ZQv4GxsbGwt7+/"
    "j3n3e3Zk2bM3mZl5w4k5Qx3w1wD3wLwF4g2kzYxY0w0uYQW8w9gP8g0wG8w0g+YxZcwb4H8gHzF7I"
    "w4QzX8g7wG8Q0g+YxZcwb4H8gHzF7Iw4QzX8g7wG8Q0g+YxZcwb4H8gHzF7I0mQx3w1wD3wLwF4g2"
    "kzYxY0w0uYQW8w9gP8g0wG8w0g+YxZcwb4H8gHzF7Iw4QzX8g7wG8Q0g+YxZcwb4H8gHzF7I0mQx3"
    "w1wD3wLwF4g2kzYxY0w0uYQW8w9gP8g0wG8w0g+YxZcwb4H8gHzF7I0mQx3w1wD3wLwF4g2kzYxY"
    "0w0uYQW8w9gP8g0wG8w0g+YxZcwb4H8gHzF7I0mQx3w1wD3wLwF4g2kzYxY0w0uYQW8w9gP8g0w"
    "G8w0g+YxZcwb4H8gHzF7I0mQx3w1wD3wLwF4g2kzYxY0w0uYQW8w9gP8g0wG8w0g+YxZcwb4H8g"
    "HzF7I0mQx3w1wD3wLwF4g2kzYxY0w0uYQW8w9gP8g0wG8w0g+YxZcwb4H8gHzF7I0mQx3w1wD3wL"
    "wF4g2kzYxY0w0uYQW8w9gP8g0wG8w0g+YxZcwb4H8gHzF7Iw4QzX8g7wG8Q0g+YxZcwb4H8gHzF7"
    "Iw4QzX8g7wG8Q0g+YxZcwb4H8gHzF7Iw4QzX8g7wG8Q0g+YxZcwb4H8gHzF7I0mQx3w1wD3wLwF4"
    "g2kzYxY0w0uYQW8w9gP8g0wG8w0g+YxZcwb4H8gHzF7I0mQx3w1wD3wLwF4g2kzYxY0w0uYQW8w"
    "9gP8g0wG8w0g+YxZcwb4H8gHzF7I0mQwAAAABJRU5ErkJggg=="
)

out_path = Path(__file__).resolve().parents[1] / 'static' / 'placeholder.png'
out_path.parent.mkdir(parents=True, exist_ok=True)
with open(out_path, 'wb') as f:
    f.write(base64.b64decode(b64))
print(f'Wrote {out_path} ({out_path.stat().st_size} bytes)')
