"""Give an oil painting a watercolor treatment.

Used to make images/rain-steam-speed-watercolor-*.jpg from the National Gallery
scan of Turner's Rain, Steam and Speed (1844) on Wikimedia Commons.

Requires: pip install numpy opencv-python-headless
Usage: python watercolor.py <input.jpg> <output.jpg> [width]
"""
import sys

import cv2
import numpy as np

src, dst = sys.argv[1], sys.argv[2]
width = int(sys.argv[3]) if len(sys.argv) > 3 else 2000
rng = np.random.default_rng(7)

img = cv2.imread(src).astype(np.float32) / 255.0
h = int(img.shape[0] * width / img.shape[1])
img = cv2.resize(img, (width, h), interpolation=cv2.INTER_AREA)


def noise(scale, octaves=4):
    """Smooth fractal noise in [0, 1], shape (h, width)."""
    out = np.zeros((h, width), np.float32)
    amp, total = 1.0, 0.0
    for o in range(octaves):
        s = max(1, int(scale / (2 ** o)))
        small = rng.random((h // s + 2, width // s + 2)).astype(np.float32)
        out += amp * cv2.resize(small, (width, h), interpolation=cv2.INTER_CUBIC)
        total += amp
        amp *= 0.5
    out /= total
    return (out - out.min()) / (out.max() - out.min())


# 1. Washes: smooth away the impasto at quarter resolution (edge-preserving, in
#    float so no banding), then bring back a little of the original structure.
small = cv2.resize(img, (width // 4, h // 4), interpolation=cv2.INTER_AREA)
for _ in range(4):
    small = cv2.bilateralFilter(small, d=9, sigmaColor=0.08, sigmaSpace=6)
washes = cv2.resize(small, (width, h), interpolation=cv2.INTER_CUBIC)
detail = cv2.GaussianBlur(img, (0, 0), 2.5)
f = washes * 0.6 + detail * 0.4

# 2. Bleed: displace along low-frequency noise so edges wander like wet paint.
dx = (noise(220) - 0.5) * 14
dy = (noise(220) - 0.5) * 14
gx, gy = np.meshgrid(np.arange(width, dtype=np.float32), np.arange(h, dtype=np.float32))
f = cv2.remap(f, gx + dx, gy + dy, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

# 3. Pigment: richer color, then lift toward the paper so it reads as transparent.
hsv = cv2.cvtColor(f, cv2.COLOR_BGR2HSV)
hsv[..., 1] = np.clip(hsv[..., 1] * 1.9, 0, 1)
f = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
paper = np.array([0.90, 0.95, 0.98], np.float32)  # BGR: warm cream
f = f * 0.88 + paper * 0.12
# A little more contrast so the darks (viaduct, engine) carry weight.
f = np.clip((f - 0.5) * 1.15 + 0.5, 0, 1)

# 4. Edge darkening only along real wash boundaries (strong, coarse edges).
gray = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY)
band = np.abs(cv2.GaussianBlur(gray, (0, 0), 1.5) - cv2.GaussianBlur(gray, (0, 0), 6))
band = np.clip((band - np.percentile(band, 80)) / (np.percentile(band, 99.5) + 1e-6), 0, 1)
band = cv2.GaussianBlur(band, (0, 0), 1.0)
f *= (1 - 0.24 * band)[..., None]

# 5. Granulation, blotchy pigment density, and cold-press paper tooth.
granulation = 1 - 0.045 * (noise(5, 2) - 0.5)
blotches = 1 - 0.10 * (noise(120, 3) - 0.5)
tooth = cv2.GaussianBlur(rng.random((h, width)).astype(np.float32), (0, 0), 0.9)
tooth = 1 - 0.05 * (tooth - tooth.mean()) / (tooth.std() + 1e-6) * 0.3
f *= (granulation * blotches * tooth)[..., None]

cv2.imwrite(dst, np.clip(f * 255, 0, 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, 84])
print(dst, width, h)
